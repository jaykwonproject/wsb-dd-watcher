import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are analyzing a Reddit DD (due diligence) post from r/wallstreetbets.
Summarize the key points into 2–3 pros and 2–3 cons, then classify the overall sentiment as one of:
Bullish, Bearish, or Mixed.
Only use the content provided; do not speculate.
Format:
Pros:
- ...
- ...

Cons:
- ...
- ...

Sentiment: ...
"""

def summarize_post(title, body):
    try:
        content = f"Title: {title}\n\nPost:\n{body}"
        chat_completion = client.chat.completions.create(
            model="gpt-4o",  # you can also use gpt-3.5-turbo if needed
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Summary Error] {e}")
        return None
