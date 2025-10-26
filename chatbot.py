import os
import time
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mistralai import Mistral


# ✅ Load API keys (make sure to set these in your environment)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTRAL_API_KEY = "frdJc5UUHsFA3K0cSAiPLRLuTIgc7k6g"

# ✅ Initialize OpenAI (fallback + non-legal)
openai_chat = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)
# ✅ Initialize new Mistral client
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

# ✅ Simple memory to hold conversation history
chat_history = []


def is_legal_query(user_input: str) -> bool:
    """Simple keyword check to decide if a query is legal/news related."""
    keywords = [
        "case", "lawsuit", "statute", "judge", "court", "contract", "legal",
        "paralegal", "lawyer", "litigation", "evidence", "precedent", "regulation",
        "compliance", "appeal", "trial", "criminal", "civil", "tort", "intellectual property"
    ]
    return any(word in user_input.lower() for word in keywords)


def mistral_chat(messages, retries=3):
    """Try Mistral first, retry on overload, fallback to OpenAI if needed."""
    for attempt in range(retries):
        try:
            response = mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": messages}]
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e).lower()
            if "capacity exceeded" in error_msg or "429" in error_msg:
                wait = (2 ** attempt) + random.random()
                print(f"⚠️ Mistral overloaded. Retrying in {wait:.1f} sec...")
                time.sleep(wait)
            else:
                print(f"⚠️ Mistral error: {e}")
                break

    # ✅ If retries fail, fallback to OpenAI
    print("🔄 Falling back to OpenAI...")
    return openai_chat.predict(messages)



def chatbot(user_input: str):
    """Main chatbot logic with routing + memory."""
    # Save user input to chat history
    chat_history.append({"role": "user", "content": user_input})

    if is_legal_query(user_input):
        # ✅ Route legal/news queries to Mistral first
        response = mistral_chat(user_input)
    else:
        # ✅ Route non-legal queries directly to OpenAI
        response = openai_chat.invoke(user_input)
        # Add disclaimer
        if hasattr(response, 'content'):
            response_text = response.content + "\n\n⚠️ Please remember: this chatbot is intended for legal/law-related questions."
        else:
            response_text = str(response) + "\n\n⚠️ Please remember: this chatbot is intended for legal/law-related questions."
        chat_history.append({"role": "bot", "content": response_text})
        return response_text

    # For legal queries, ensure response is a string
    if hasattr(response, 'content'):
        response_text = response.content
    else:
        response_text = str(response)
    chat_history.append({"role": "bot", "content": response_text})
    return response_text


# ✅ Interactive loop
if __name__ == "__main__":
    print("🤖 Legal Assistant Chatbot (Mistral + OpenAI Fallback)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            print("👋 Goodbye!")
            break
        response = chatbot(user_input)
        print("Bot:", response)


# # chatbot.py

# from langchain_community.chat_models import ChatOpenAI
# from langchain_mistralai import ChatMistralAI
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate
# from langchain.memory import ConversationBufferMemory

# # -----------------------------
# # 1️⃣ Initialize models
# # -----------------------------

# # ChatGPT handles general conversation
# chatgpt = ChatOpenAI(
#     model_name="gpt-3.5-turbo",
#     temperature=0.2
# )

# # Mistral handles legal case/news responses
# mistral = ChatMistralAI(
#     model="mistral-medium-latest",
#     temperature=0,
#     api_key="w9yDGXls7kEYi5LLj6YatcvfefV76U3F"
# )

# # -----------------------------
# # 2️⃣ Create memory
# # -----------------------------
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# # -----------------------------
# # 3️⃣ Define prompts
# # -----------------------------

# # Prompt for Mistral: legal answer
# mistral_prompt = PromptTemplate(
#     template=(
#         "You are a legal research assistant. Answer the user's query "
#         "based on current legal cases, precedents, and news relevant to law. "
#         "If the query is unrelated to law, respond briefly and remind the user: "
#         "'Please ask questions relevant to legal cases or law.'\n\n"
#         "User Query: {query}"
#     ),
#     input_variables=["query"]
# )

# # Prompt for ChatGPT: conversational tone using memory + Mistral output
# chatgpt_prompt = PromptTemplate(
#     template=(
#         "You are a helpful assistant chatbot for a law firm. Keep conversation friendly and concise. "
#         "Use the output from Mistral for legal answers when relevant.\n\n"
#         "Conversation so far:\n{chat_history}\n\n"
#         "User: {user_input}\n"
#         "Assistant:"
#     ),
#     input_variables=["chat_history", "user_input"]
# )

# # -----------------------------
# # 4️⃣ Create chains
# # -----------------------------

# # Chain for Mistral
# mistral_chain = LLMChain(
#     llm=mistral,
#     prompt=mistral_prompt,
#     output_key="mistral_answer"
# )

# # Chain for ChatGPT
# chatgpt_chain = LLMChain(
#     llm=chatgpt,
#     prompt=chatgpt_prompt,
#     output_key="final_response"
# )

# # -----------------------------
# # 5️⃣ Interactive loop
# # -----------------------------
# print("⚖️ Law Firm Chatbot (ChatGPT + Mistral) ready. Type 'exit' to quit.\n")

# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ["exit", "quit"]:
#         print("Bot: Goodbye! 👋")
#         break

#     # Step 1: Mistral generates legal answer
#     mistral_answer = mistral_chain.run(query=user_input)

#     # Step 2: ChatGPT produces conversational response using memory + Mistral output
#     final_response = chatgpt_chain.run(
#         chat_history=memory.buffer if hasattr(memory, "buffer") else "",
#         user_input=f"{user_input}\n\nMistral Answer: {mistral_answer}"
#     )

#     # Step 3: Save conversation to memory
#     memory.chat_memory.add_user_message(user_input)
#     memory.chat_memory.add_ai_message(final_response)

#     # Step 4: Display response
#     print(f"Bot: {final_response}\n")
