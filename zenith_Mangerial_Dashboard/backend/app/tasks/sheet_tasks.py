"""
Celery tasks for Excel sheet processing.

This module provides background tasks for processing weekly status Excel sheets.
Each task calls file-specific processor modules that use the helper functions.
"""

from app.core.logging import get_logger
from app.workers.celery_app import celery_app
from app.engine.sheets.helper import get_sheet_summary

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.sheet_tasks.process_status_sheet",
    max_retries=3,
    default_retry_delay=60,
)
def process_status_sheet(
    self,
    file_path: str,
    processor_module: str,
    du_file_path: str = "DU.xlsx",
    **kwargs
) -> dict:
    """
    Process a single Excel status sheet using a file-specific processor.
    
    Args:
        file_path: Path to the Excel file to process
        processor_module: Module path to the file-specific processor (e.g., 'app.engine.sheets.plateformteam')
        du_file_path: Path to DU.xlsx for offboarded vlinkers
        **kwargs: Additional arguments to pass to the processor
        
    Returns:
        Dictionary with processing results
    """
    logger.info(
        "Processing status sheet",
        task_id=self.request.id,
        file_path=file_path,
        processor_module=processor_module
    )
    
    try:
        # Dynamically import the processor module
        module = __import__(processor_module, fromlist=['process_file'])
        result = module.process_file(file_path, du_file_path=du_file_path, **kwargs)
        
        logger.info(
            "Sheet processing completed",
            task_id=self.request.id,
            file_path=file_path,
            total_unfilled=result.get('total_unfilled', 0)
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Sheet processing failed",
            task_id=self.request.id,
            file_path=file_path,
            error=str(e)
        )
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    name="app.tasks.sheet_tasks.process_multiple_sheets",
    max_retries=3,
    default_retry_delay=60,
)
def process_multiple_sheets(
    self,
    file_configs: list,
    du_file_path: str = "DU.xlsx"
) -> dict:
    """
    Process multiple Excel files using their respective processors.
    
    Args:
        file_configs: List of dicts with 'file_path' and 'processor_module' keys
        du_file_path: Path to DU.xlsx for offboarded vlinkers
        
    Returns:
        Dictionary with combined processing results
    """
    logger.info(
        "Processing multiple status sheets",
        task_id=self.request.id,
        file_count=len(file_configs)
    )
    
    try:
        results = []
        
        for config in file_configs:
            file_path = config.get('file_path')
            processor_module = config.get('processor_module')
            kwargs = config.get('kwargs', {})
            
            try:
                module = __import__(processor_module, fromlist=['process_file'])
                result = module.process_file(file_path, du_file_path=du_file_path, **kwargs)
                result['file_path'] = file_path
                results.append(result)
            except Exception as e:
                results.append({
                    'file_path': file_path,
                    'error': str(e),
                    'status': 'failed'
                })
        
        total_unfilled = sum(
            result.get('total_unfilled', 0) 
            for result in results 
            if 'total_unfilled' in result
        )
        
        logger.info(
            "Multiple sheets processing completed",
            task_id=self.request.id,
            files_processed=len(results),
            total_unfilled=total_unfilled
        )
        
        return {
            'files_processed': len(results),
            'total_unfilled': total_unfilled,
            'results': results
        }
        
    except Exception as e:
        logger.error(
            "Multiple sheets processing failed",
            task_id=self.request.id,
            error=str(e)
        )
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    name="app.tasks.sheet_tasks.get_sheet_info",
    max_retries=2,
    default_retry_delay=30,
)
def get_sheet_info(self, file_path: str) -> dict:
    """
    Get summary information about sheets in an Excel file.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Dictionary with sheet information
    """
    logger.info(
        "Getting sheet information",
        task_id=self.request.id,
        file_path=file_path
    )
    
    try:
        summary = get_sheet_summary(file_path)
        logger.info(
            "Sheet information retrieved",
            task_id=self.request.id,
            total_sheets=summary.get('total_sheets', 0)
        )
        return summary
        
    except Exception as e:
        logger.error(
            "Failed to get sheet information",
            task_id=self.request.id,
            file_path=file_path,
            error=str(e)
        )
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    name="app.tasks.sheet_tasks.weekly_status_check",
    max_retries=3,
    default_retry_delay=60,
)
def weekly_status_check(
    self,
    file_configs: list,
    du_file_path: str = "DU.xlsx"
) -> dict:
    """
    Scheduled task to check weekly status updates across all team sheets.
    This is designed to run on a schedule (e.g., every Friday evening).
    
    Args:
        file_configs: List of dicts with 'file_path' and 'processor_module' keys
        du_file_path: Path to DU.xlsx for offboarded vlinkers
        
    Returns:
        Dictionary with summary of all processing results
    """
    logger.info(
        "Starting weekly status check",
        task_id=self.request.id,
        file_count=len(file_configs)
    )
    
    try:
        results = []
        
        for config in file_configs:
            file_path = config.get('file_path')
            processor_module = config.get('processor_module')
            kwargs = config.get('kwargs', {})
            
            try:
                module = __import__(processor_module, fromlist=['process_file'])
                result = module.process_file(file_path, du_file_path=du_file_path, **kwargs)
                result['file_path'] = file_path
                results.append(result)
            except Exception as e:
                results.append({
                    'file_path': file_path,
                    'error': str(e),
                    'status': 'failed'
                })
        
        # Aggregate statistics
        stats = {
            'total_files': len(results),
            'successful_files': 0,
            'failed_files': 0,
            'total_team_leads': 0,
            'total_unfilled_entries': 0,
            'files_with_unfilled': 0,
            'offboarded_vlinkers': 0
        }
        
        detailed_results = []
        
        for result in results:
            if 'error' in result or result.get('status') == 'failed':
                stats['failed_files'] += 1
                detailed_results.append({
                    'file': result.get('file_path'),
                    'status': 'failed',
                    'error': result.get('error')
                })
            else:
                stats['successful_files'] += 1
                stats['total_team_leads'] += len(result.get('team_leads', []))
                stats['total_unfilled_entries'] += result.get('total_unfilled', 0)
                stats['offboarded_vlinkers'] = result.get('offboarded_count', 0)
                
                if result.get('total_unfilled', 0) > 0:
                    stats['files_with_unfilled'] += 1
                
                detailed_results.append({
                    'file': result.get('file_path'),
                    'sheet': result.get('sheet_name'),
                    'status': 'success',
                    'sheet_type': result.get('sheet_type'),
                    'team_leads': len(result.get('team_leads', [])),
                    'unfilled_count': result.get('total_unfilled', 0),
                    'unfilled_details': result.get('unfilled_status', [])[:10]  # Limit details
                })
        
        logger.info(
            "Weekly status check completed",
            task_id=self.request.id,
            stats=stats
        )
        
        return {
            'summary': stats,
            'details': detailed_results
        }
        
    except Exception as e:
        logger.error(
            "Weekly status check failed",
            task_id=self.request.id,
            error=str(e)
        )
        raise self.retry(exc=e)
