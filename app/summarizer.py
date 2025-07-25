import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are analyzing a Reddit DD (due diligence) post from r/wallstreetbets.

Your task:
1. Begin with a one-sentence TL;DR summary.
2. Extract 2–3 concise "Pros" and 2–3 "Cons" based only on what is explicitly stated.
3. Identify the *primary* stock ticker the post is mainly focused on. Only return ONE ticker in uppercase. If no clear ticker is the main focus, return "None".
4. Determine overall sentiment: Bullish, Bearish, or Mixed — based on OP's tone and reasoning, not just the facts.

⚠️ DO NOT list multiple tickers. Even if the post mentions several, extract only the one most discussed or analyzed.
⚠️ DO NOT speculate beyond the content. Only summarize what’s written.

Format strictly as:

Sentiment: <Bullish|Bearish|Mixed>  
Ticker: <TSLA or None>  

TL;DR: <short one-sentence summary>

Pros:
- ...

Cons:
- ...
"""


def summarize_post(title, body):
    try:
        content = f"Title: {title}\n\nPost:\n{body}"
        chat_completion = client.chat.completions.create(
            model="gpt-4o",  # or gpt-3.5-turbo if needed
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content}
            ],
            temperature=0.7,
            max_tokens=600
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Summary Error] {e}")
        return None
