import json
import os
from prompts import assistant_instructions

def create_assistant(client):
  assistant_file_path = 'assistant.json'

  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:

    vector_store = client.beta.vector_stores.create(name="Knowledge Documents")
    file_paths = ["knowledge/doc1.docx", "knowledge/doc2.docx", "knowledge/doc3.docx", "knowledge/doc4.docx", "knowledge/doc5.docx", "knowledge/doc6.docx", "knowledge/doc7.docx", "knowledge/doc8.docx", "knowledge/doc9.docx", "knowledge/doc10.docx", "knowledge/doc11.docx", "knowledge/doc12.docx", "knowledge/doc13.docx", "knowledge/doc14.docx", "knowledge/doc15.docx", "knowledge/doc16.docx", "knowledge/doc17.docx", "knowledge/doc18.docx", "knowledge/doc19.docx", "knowledge/doc20.docx", "knowledge/doc21.docx", "knowledge/doc22.docx", "knowledge/doc23.docx", "knowledge/doc24.docx"]

    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
      vector_store_id=vector_store.id, files=file_streams
    )

    print(file_batch.status)
    print(file_batch.file_counts)

    assistant = client.beta.assistants.create(
      instructions = assistant_instructions,
      model="gpt-4o",
      tools=[{"type": "file_search"}],
      tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id