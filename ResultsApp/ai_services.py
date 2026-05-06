from openai import OpenAI

client = OpenAI()

def generate_lesson_plan(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"AI service is currently unavailable. Reason: {str(e)}"