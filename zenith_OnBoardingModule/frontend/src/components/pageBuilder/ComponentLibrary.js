// Component Library - Available components for page builder
export const componentLibrary = [
  {
    id: 'container',
    name: 'Container',
    icon: 'view_quilt',
    category: 'layout',
    description: 'A flexible container for grouping content',
    defaultProps: {
      padding: 'md',
      margin: 'none',
      backgroundColor: 'transparent',
      borderRadius: 'none'
    }
  },
  {
    id: 'section',
    name: 'Section',
    icon: 'segment',
    category: 'layout',
    description: 'A section with heading and content area',
    defaultProps: {
      title: 'Section Title',
      padding: 'lg',
      backgroundColor: 'dark'
    }
  },
  {
    id: 'card',
    name: 'Card',
    icon: 'style',
    category: 'content',
    description: 'A card component for displaying content',
    defaultProps: {
      title: 'Card Title',
      content: 'Card content goes here',
      padding: 'md',
      backgroundColor: 'dark'
    }
  },
  {
    id: 'button',
    name: 'Button',
    icon: 'smart_button',
    category: 'interactive',
    description: 'A clickable button',
    defaultProps: {
      label: 'Click Me',
      color: 'primary',
      size: 'md',
      outline: false
    }
  },
  {
    id: 'text',
    name: 'Text',
    icon: 'title',
    category: 'content',
    description: 'Text content',
    defaultProps: {
      content: 'Your text here',
      variant: 'body1',
      color: 'white'
    }
  },
  {
    id: 'heading',
    name: 'Heading',
    icon: 'format_size',
    category: 'content',
    description: 'Heading text',
    defaultProps: {
      content: 'Heading',
      level: 'h4',
      color: 'white'
    }
  },
  {
    id: 'image',
    name: 'Image',
    icon: 'image',
    category: 'media',
    description: 'Image display',
    defaultProps: {
      src: '',
      alt: 'Image',
      contain: false
    }
  },
  {
    id: 'divider',
    name: 'Divider',
    icon: 'horizontal_rule',
    category: 'layout',
    description: 'Horizontal divider line',
    defaultProps: {
      color: 'grey-6',
      inset: false
    }
  },
  {
    id: 'spacer',
    name: 'Spacer',
    icon: 'space_bar',
    category: 'layout',
    description: 'Vertical spacing',
    defaultProps: {
      size: 'md'
    }
  },
  {
    id: 'grid',
    name: 'Grid',
    icon: 'grid_on',
    category: 'layout',
    description: 'Grid layout container',
    defaultProps: {
      columns: 2,
      gap: 'md'
    }
  },
  {
    id: 'input',
    name: 'Input Field',
    icon: 'input',
    category: 'form',
    description: 'Text input field',
    defaultProps: {
      label: 'Input',
      placeholder: 'Enter text',
      outlined: true
    }
  },
  {
    id: 'select',
    name: 'Select Dropdown',
    icon: 'arrow_drop_down',
    category: 'form',
    description: 'Dropdown selection',
    defaultProps: {
      label: 'Select',
      options: ['Option 1', 'Option 2', 'Option 3'],
      outlined: true
    }
  },
  {
    id: 'checkbox',
    name: 'Checkbox',
    icon: 'check_box',
    category: 'form',
    description: 'Checkbox input',
    defaultProps: {
      label: 'Checkbox label',
      color: 'primary'
    }
  },
  {
    id: 'chart',
    name: 'Chart',
    icon: 'bar_chart',
    category: 'data',
    description: 'Data visualization chart',
    defaultProps: {
      type: 'bar',
      title: 'Chart Title'
    }
  },
  {
    id: 'table',
    name: 'Table',
    icon: 'table_chart',
    category: 'data',
    description: 'Data table',
    defaultProps: {
      columns: ['Column 1', 'Column 2', 'Column 3'],
      rows: 3
    }
  }
]

export const componentCategories = [
  { id: 'layout', name: 'Layout', icon: 'view_quilt' },
  { id: 'content', name: 'Content', icon: 'description' },
  { id: 'interactive', name: 'Interactive', icon: 'touch_app' },
  { id: 'media', name: 'Media', icon: 'perm_media' },
  { id: 'form', name: 'Form', icon: 'edit_note' },
  { id: 'data', name: 'Data', icon: 'analytics' }
]
