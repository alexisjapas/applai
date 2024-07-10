import requests
import re
import ollama
import json
import subprocess
import os

def ollama_chat(preprompt: str, prompt: str, data: str, language: str, model: str, temperature: float):
    preprompt = (
        f"Assume your interlocutor speaks {language}. Answer using only {language}.\n" +
        "Always provide direct, concise answers to questions. Do not include introductory phrases or explanations.\n"
        + preprompt
    )
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": preprompt,
            },
            {
                "role": "user",
                "content": f"[Data]\n===\n{data}\n===\n\n [Request]\n{prompt}",
            },
        ],
        options={  # https://github.com/ollama/ollama/blob/main/docs/modelfile.md#parameter
            "temperature": temperature,
        },
    )
    return response["message"]["content"]


def fetch_data(url: str) -> str:
    # PREPARING CURL
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    return response.text


def html_extract_content(data: str) -> str:
    print(len(data))

    # HTML body
    regex_body = r"<body[^>]*>(.*?)</body>"
    body = re.search(regex_body, data, re.DOTALL).group(1)
    print(len(body))

    # Script tags
    regex_script = re.compile(r"<script.*?>.*?</script>", re.DOTALL)
    body_without_scripts = regex_script.sub("", body)
    print(len(body_without_scripts))

    # HTML tags
    regex_tags = re.compile(r"<[^>]+>")
    body_without_tags = regex_tags.sub("", body_without_scripts)
    print(len(body_without_tags))

    # Spaces
    content = re.sub(r"\s", " ", body_without_tags)
    content = re.sub(r" {3,}", "\n", content)

    # Strip leading and trailing whitespace from the content
    content = content.strip()
    print(len(content))

    return content


def summarize_position_data(position_data: str, language:str, model: str) -> dict:
    print(f"Summarising position's data with {model}, please wait...")

    # AI summary
    preprompt = "If the information is not in the text, answer 'N/A'."
    temperature = 0.05
    position_dict = {
        "job_title": ollama_chat(
            preprompt=preprompt,
            prompt=f"What is the exact title of the position in the provided data?",
            data=position_data,
            language=language,
            model=model,
            temperature=temperature,
        ),
        "company": ollama_chat(
            preprompt=preprompt,
            prompt=f"What is the name of the company offering the position in the provided data?",
            data=position_data,
            language=language,
            model=model,
            temperature=temperature,
        ),
        "missions": ollama_chat(
            preprompt=preprompt,
            prompt=f"Describe the mission(s) of the position in the provided data.",
            data=position_data,
            language=language,
            model=model,
            temperature=temperature,
        ),
        "tasks": ollama_chat(
            preprompt=preprompt,
            prompt=f"Describe the task(s) of the position in the provided data.",
            data=position_data,
            language=language,
            model=model,
            temperature=temperature,
        ),
        "skills": ollama_chat(
            preprompt=preprompt,
            prompt=f"List the skills required for the position in the provided data.",
            data=position_data,
            language=language,
            model=model,
            temperature=temperature,
        ),
        "experience": ollama_chat(
            preprompt=preprompt,
            prompt=f"What is the required experience for the position in the provided data.",
            data=position_data,
            language=language,
            model=model,
            temperature=temperature,
        ),
        "recruiters": ollama_chat(
            preprompt=preprompt,
            prompt=f"List the names of the recruiters of the position in the provided data. Do not include any information about the recruiters, like email or phone number.",
            data=position_data,
            language=language,
            model=model,
            temperature=temperature,
        ),
        "location": "",
        "contract_type": "",
        "start_date": "",
        "salary": "",
        "benefits": "",
        # "location": ollama_chat(
        #     preprompt=preprompt,
        #     prompt="Where is located the position in the provided data?",
        #     data=position_data,
        #     language=language,
        #     model=model,
        #     temperature=temperature,
        # ),
        # "contract_type": ollama_chat(
        #     preprompt=preprompt,
        #     prompt="What is the type of contract and if applicable, the duration, for the position in the provided data?",
        #     data=position_data,
        #     language=language,
        #     model=model,
        #     temperature=temperature,
        # ),
        # "start_date": ollama_chat(
        #     preprompt=preprompt,
        #     prompt="What is the start date for the position in the provided data?",
        #     data=position_data,
        #     language=language,
        #     model=model,
        #     temperature=temperature,
        # ),
        # "salary": ollama_chat(
        #     preprompt=preprompt,
        #     prompt="What is the salary for the position in the provided data?",
        #     data=position_data,
        #     language=language,
        #     model=model,
        #     temperature=temperature,
        # ),
        # "benefits": ollama_chat(
        #     preprompt=preprompt,
        #     prompt="If applicable, indicate benefits other than salary.",
        #     data=position_data,
        #     language=language,
        #     model=model,
        #     temperature=temperature,
        # ),
    }

    return position_dict


def generate_cover_letter(position_data: str, user_data: dict, language: str, model: str) -> str:
    print(f"Generating the cover letter with {model}, please wait...")

    # Generating
    preprompt = "Assume that the user has provided full information about their skills and experience; avoid inventing or overstating the user's qualifications, skills and experience."
    prompt_cover_letter = "Write a cover letter for the position presented in the provided data. Incorporate my skills, experiences, and personal data that are relevant to the role to craft a compelling letter. Omit the header, salutations and signoff, and concentrate on the core content of the letter."
    data = f"[User]\n\
        ---\n\
        {user_data}\n\
        ---\n\
        \n\
        [Position]\n\
        ---\n\
        {position_data}\n\
        ---"
    cover_letter = ollama_chat(
        preprompt=preprompt,
        prompt=prompt_cover_letter,
        data=data,
        language=language,
        model=model,
        temperature=0.1,
    )
    return cover_letter


def export_cover_letter(
    details: dict,
    position_data: dict,
    cover_letter_content: str,
    language: str,
    application_folder: str,
    output_type: str,
) -> None:
    # Fill typst files
    na_recruiters = "recruiters" if language == "english" else "recruteurs"
    recruiters = (
        na_recruiters
        if position_data["recruiters"] == "N/A"
        else position_data["recruiters"]
    )
    CONTENT_PATH = os.path.join("typst", "content")
    if not os.path.exists(CONTENT_PATH):
        os.mkdir(CONTENT_PATH)
    with open(os.path.join(CONTENT_PATH,"name.typ"), "w", encoding="utf-8") as file:
        file.write(f"{details['first_name']} {details['surname']}")
    with open(os.path.join(CONTENT_PATH,"email.typ"), "w", encoding="utf-8") as file:
        file.write(details["email"].replace("@", r"\@"))
    with open(os.path.join(CONTENT_PATH,"phone_number.typ"), "w", encoding="utf-8") as file:
        file.write(details["phone_number"])
    with open(os.path.join(CONTENT_PATH,"salutations.typ"), "w", encoding="utf-8") as file:
        file.write(f"{'Dear' if language == 'english' else 'Cher'} {recruiters},")
    with open(os.path.join(CONTENT_PATH,"content.typ"), "w", encoding="utf-8") as file:
        file.write(cover_letter_content)
    with open(os.path.join(CONTENT_PATH,"greeting.typ"), "w", encoding="utf-8") as file:
        file.write('Sincerely,' if language == 'english' else 'Cordialement,')
    # Compile file
    command = [
        "typst",
        "compile",
        "typst/main.typ",
        f"{application_folder}/cover_letter.{output_type}",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    # Check the return code
    if result.returncode == 0:
        print("Command executed successfully.")
    else:
        print(f"Command failed with return code {result.returncode}.")
        print("Output:", result.stdout)
        print("Error:", result.stderr)


def export_cover_letter_for_pipeline(
    user_data: dict,
    position_data: dict,
    cover_letter_content: str,
    application_folder: str,
    output_type: str,
) -> None:
    # Fill typst files
    details = user_data["details"]
    recruiters = (
        "recruiters"
        if position_data["recruiters"] == "N/A"
        else position_data["recruiters"]
    )
    with open("typst/name.typ", "w") as file:
        file.write(f"{details['first_name']} {details['surname']}")
    with open("typst/email.typ", "w") as file:
        file.write(details["email"].replace("@", r"\@"))
    with open("typst/phone.typ", "w") as file:
        file.write(details["phone"])
    with open("typst/salutations.typ", "w") as file:
        file.write(f"Dear {recruiters},")
    with open("typst/content.typ", "w") as file:
        file.write(cover_letter_content)

    # Compile file
    command = [
        "typst",
        "compile",
        "typst/main.typ",
        f"{application_folder}/cover_letter.{output_type}",
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    # Check the return code
    if result.returncode == 0:
        print("Command executed successfully.")
    else:
        print(f"Command failed with return code {result.returncode}.")
