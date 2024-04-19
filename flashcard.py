import config
import transcript
from openai import OpenAI
import tiktoken

SYSTEM_PROMPT = "You are a flashcard generator. You generate questions and answers that are key to understanding the transcripts given to you."
TEMPERATURE = 0
MODEL = "gpt-3.5-turbo"

client = OpenAI(api_key=config.OPENAI_KEY)
encoding = tiktoken.encoding_for_model(MODEL)

class Flashcard:
    def __init__(self, question, answer):
        self.content = {
            "question": question,
            "answer": answer
        }
        print(f"Flashcard generated. Question: {question}, Answer: {answer}")

    def return_dict(self):
        return self.content

#split text into list of chunks with x token length
def split_text(text, chunk_length) -> list[str]:
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_length):
        chunks.append(encoding.decode(tokens[i:i+chunk_length]))
    return chunks

#remove output formatting
def clean_text(text) -> str:
    text = text.replace('\n', "")
    text = text.replace('Q: ', "")
    text = text.replace('A: ', "")
    return text

#generate flash cards from transcript text
def generate_flashcards(texts : list[str], count_per_chunk, difficulty = 2, temp = TEMPERATURE, system_prompt = SYSTEM_PROMPT, model = MODEL) -> list[Flashcard]:
    outputs = []
    difficulty_options = ["Very easy", "Average", "Expert"]
    #generate questions/answers
    for text in texts:
        if len(outputs) == 0:
            prompt = f"Generate {count_per_chunk} concise flashcard questions and answers to aid in retaining the key insights from the video transcript provided below. The questions should pertain solely to the primary subject matter of the video and should be designed to enhance learning. Avoid questions regarding the speaker, channel, sponsors, or ancillary information. The difficulty of the questions should be set to:  {difficulty_options[difficulty-1]}. Generate the flashcards in the language of the transcript. \n Desired format: \n Q: <question>, A: <answer> \n Transcript: ### {text} ###"
        else:
            prompt = f"Generate {count_per_chunk} concise flashcard questions and answers to aid in retaining the key insights from the video transcript provided below. The questions should pertain solely to the primary subject matter of the video and should be designed to enhance learning. Avoid questions regarding the speaker, channel, sponsors, or ancillary information. Only generate questions and answers that haven't already been generated. The difficulty of the questions should be set to: {difficulty_options[difficulty-1]}. Generate the flashcards in the language of the transcript. \n Already Generated: {outputs[:-1]}  \n Desired format: \n Q: <question>, A: <answer> \n Transcript: ### {text} ###"
        
        outputs.append(client.chat.completions.create(
            model=model,
            temperature=temp,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        ).choices[0].message.content)
 
    #split into question/answer pairs
    qa_list = []
    for output in outputs:
        qa_list.extend(output.split("Q:"))

    for i in range(len(qa_list)):
        qa_list[i] = qa_list[i].split("A:")

    qa_list = [qa for qa in qa_list if qa != [""]] #remove any empties 

    #assign to flashcard instances
    flashcards = []
    for i in range(len(qa_list)): 
        flashcards.append(Flashcard(clean_text(qa_list[i][0]), clean_text(qa_list[i][1]))) 

    return flashcards

if __name__ == "__main__":
    video_transcript = transcript.get_transcript("bjL-Z7fW2FM")
    print(generate_flashcards(split_text(video_transcript, 3900), 2))

