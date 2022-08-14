from presenters.pending_documents_presenter import PendingDocumentsPresenter

presenter = PendingDocumentsPresenter.get()
for document in presenter["pending_boletas"]:
    print(f"Boletas generadas: {document['Boletas generadas']}")
    print(f"Nombre cliente: {document['Nombre cliente']}")
    print(f"Reserva efectiva: {document['Reserva efectiva']}")
