from pdf_chatbot import PDFChatbot

if __name__ == '__main__':
    print('Instantiating PDFChatbot...')
    cb = PDFChatbot()
    print('Instance created')
    print('Checking for existing vector store...')
    loaded = cb.load_existing_vector_store()
    print('load_existing_vector_store returned:', loaded)
