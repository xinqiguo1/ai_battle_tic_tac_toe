from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

class GameAnswer(BaseModel):
    move: str = Field(pattern=r"^[ABC][123]$")

def call_chatgpt(user_prompt: str) -> tuple[str, str | None]:
    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[
            {"role": "system", "content": """You are a Tic Tac Toe move generator.
Rules:
- Game is 3x3 with coordinates: rows 1,2,3 and columns A,B,C.
- I will provide the current board state and the list of legal moves.
- You must choose exactly one legal move.
- You are playing as the mark I specify (X or O).

Output format (strict):
- You must respond with a JSON object containing a "move" field with the coordinate (e.g., {"move": "B2"}).
- The move must match the pattern [ABC][123].
- Also include a "reasoning" field explaining your thought process."""},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    
    content = response.choices[0].message.content
    
    try:
        data = json.loads(content)
        move = data.get("move", "")
        reasoning_summary = data.get("reasoning", "No reasoning provided.")
        
        if not move or len(move) != 2 or move[0] not in "ABC" or move[1] not in "123":
            raise ValueError(f"Invalid move format: {move}")
            
        return move, reasoning_summary
    except (json.JSONDecodeError, ValueError) as e:
        raise RuntimeError(f"Failed to parse model response: {content}. Error: {e}")

user_prompt_base = """You are X.

Coordinates:
Rows: 1,2,3
Cols: A,B,C

Board:
A1 B1 C1
A2 B2 C2
A3 B3 C3

Your turn. Output one move only.

Here is the board state:

"""

if __name__ == "__main__":
    board_state = """
    A1=O, B1=., C1=X
    A2=X, B2=., C2=O
    A3=O, B3=X, C3=.
    """

    move, summary = call_chatgpt(user_prompt_base + board_state)

    print("Move:", move)
    print("\n🧠 Reasoning Summary:\n", summary or "No reasoning summary found.")
