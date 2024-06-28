from flask import Flask, render_template, url_for, request, redirect, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from db_models import *
import process
import os
import time
import json


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///applai.db"
db.init_app(app)
BASE_DIR = os.getcwd()
APPLICATIONS_DIR = os.path.join(BASE_DIR, "static", "applications")
TEST_MODE = False
MODELS = {
    "llama": "llama3:8b-instruct-q5_K_M",           # 5.7 GB
    "mistral": "mistral:7b-instruct-q5_K_M",        # 5.1 GB
    "gemma": "gemma:2b-instruct-q2_K"               # 1.3 GB
}
selected_model = "llama"
LANGUAGES = {
    "english": "english",
    "french": "french"
}
selected_language = "english"

with app.app_context():
    db.create_all()


@app.route("/", methods=["POST", "GET"])
def index():
    user = UserDb.query.first()
    models = []
    for model in MODELS:
        models.append(model)
    languages = []
    for language in LANGUAGES:
        languages.append(language)

    if (user) == None:
        user = UserDb(
            first_name="",
            surname="",
            address="",
            city="",
            postal_code="",
            country="",
            phone_number="",
            email="",
        )
        try:
            db.session.add(user)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"An error occured during the app initialization. Please reload the homepage: {e}"
    applications = GenerationRequestDb.query.order_by(GenerationRequestDb.date).all()
    return render_template(
        "index.html",
        user=user,
        applications=applications,
        models=models,
        selected_model=selected_model,
        languages=languages,
        selected_language=selected_language
    )


@app.route("/user", methods=["POST"])
def user():
    print(request.form)
    first_name = request.form["first_name"]
    surname = request.form["surname"]
    email = request.form["email"]
    phone_number = request.form["phone_number"]
    address = request.form["address"]
    city = request.form["city"]
    postal_code = request.form["postal_code"]
    country = request.form["country"]    

    user = UserDb(
        id=1,
        first_name=first_name,
        surname=surname,
        email=email,
        phone_number=phone_number,
        address=address,
        city=city,
        postal_code=postal_code,
        country=country,
    )

    try:
        db.session.merge(user)  # Add instead to enable multiple users
        db.session.commit()

        # Create a new DataDb object for the language
        data = DataDb(
            language=selected_language,
            user_id=user.id,
            title=request.form["title"],
            description=request.form["description"]
        )  # TODO Add language change
        db.session.merge(data)  # Add instead to enable multiple languages
        db.session.commit()

        # Handle links
        LinkDb.query.filter_by(data_language=data.language).delete()
        for key, value in request.form.items():
            if (
                key.startswith("link-") and value
            ):  # Ensure it's a link input and not empty
                new_link = LinkDb(
                    data_language=data.language,
                    link=value
                )
                db.session.add(new_link)

        db.session.commit()

        # Handle languages
        LanguageDb.query.filter_by(data_language=data.language).delete()
        for key, value in request.form.items():
            if (
                key.startswith("language-") and value
            ):  # Ensure it's a language input and not empty
                new_language = LanguageDb(
                    data_language=data.language,
                    language=value
                )
                db.session.add(new_language)

        db.session.commit()

        # Handle additional skills
        AdditionalSkillDb.query.filter_by(data_language=data.language).delete()
        for key, value in request.form.items():
            if (
                key.startswith("additional_skill-") and value
            ):  # Ensure it's a additional_skill input and not empty
                new_additional_skill = AdditionalSkillDb(
                    data_language=data.language,
                    additional_skill=value
                )
                db.session.add(new_additional_skill)

        db.session.commit()

        # Handle educations
        EducationDb.query.filter_by(data_language=data.language).delete()
        for key, value in request.form.items():
            if (
                key.startswith("education-") and value
            ):  # Ensure it's a education input and not empty
                new_education = EducationDb(
                    data_language=data.language,
                    education=value
                )
                db.session.add(new_education)

        db.session.commit()

        # Handle experiences
        ExperienceDb.query.filter_by(data_language=data.language).delete()
        for key, value in request.form.items():
            if (
                key.startswith("experience-") and value
            ):  # Ensure it's a experience input and not empty
                new_experience = ExperienceDb(data_language=data.language, experience=value)
                db.session.add(new_experience)

        db.session.commit()

        return redirect("/")
    except Exception as e:
        db.session.rollback()
        return f"An error occured: {e}"


@app.route("/select_model", methods=["POST"])
def selectModel():
    global selected_model
    selected_model = request.form.get("model_select")
    return redirect("/")


@app.route("/select_language", methods=["POST"])
def selectLanguage():
    global selected_language
    selected_language = request.form.get("language_select")
    return redirect("/")


@app.route("/generate", methods=["POST"])
def generateRequest():
    # TODO better controls especially with the try/except (and if we need both GenerationRequestDb and GenerationDb or only GenerationDb)
    # User data
    user = UserDb.query.first()
    user_data = {}
    for field in user.__table__.columns:
        user_data[field.name] = getattr(user, field.name)

    if (TEST_MODE) == True:
        time.sleep(3)
    else:
        url = request.form["url"]

        if GenerationRequestDb.query.filter_by(url=url).first():
            print("You already applied to this offer.")
        else:
            # Position data
            position_html = process.fetch_data(url)
            position_content = process.html_extract_content(position_html)
            position_data = process.summarize_position_data(
                position_data=position_content,
                language=LANGUAGES[selected_language],
                model=MODELS[selected_model]
            )
            cover_letter_content = process.generate_cover_letter(
                position_data=position_data,
                user_data=user_data,
                language=LANGUAGES[selected_language],
                model=MODELS[selected_model]
            )

            new_generation = GenerationRequestDb(
                url=url,
                job_title=position_data["job_title"],
                company=position_data["company"],
                missions=position_data["missions"],
                tasks=position_data["tasks"],
                skills=position_data["skills"],
                experience=position_data["experience"],
                recruiters=position_data["recruiters"],
                location=position_data["location"],
                contract_type=position_data["contract_type"],
                start_date=position_data["start_date"],
                salary=position_data["salary"],
                benefits=position_data["benefits"],
                cover_letter=cover_letter_content,
            )
            try:
                db.session.add(new_generation)
                db.session.commit()
                new_application_dir = os.path.join(
                    APPLICATIONS_DIR, str(user.id), str(new_generation.id)
                )
                os.makedirs(new_application_dir, exist_ok=True)
                process.export_cover_letter(
                    details=user_data,
                    position_data=position_data,
                    cover_letter_content=cover_letter_content,
                    language=LANGUAGES[selected_language],
                    application_folder=new_application_dir,
                    output_type="svg",
                )
                return redirect("/")
            except Exception as e:
                return f"An error occured: {e}"
    return redirect("/")


@app.route("/application/<int:application_id>", methods=["GET"])
def get_application(application_id):
    application = GenerationRequestDb.query.get(application_id)
    if not application:
        return jsonify({"error": "Application not found"}), 404

    application_data = {
        "job_title": application.job_title,
        "company": application.company,
        "recruiters": application.recruiters,
        "location": application.location,
        "contract_type": application.contract_type,
        "start_date": application.start_date,
        "salary": application.salary,
        "benefits": application.benefits,
        "cover_letter": application.cover_letter,
        "cover_letter_img": url_for('static', filename=f'applications/1/{application.id}/cover_letter.svg'),
    }
    return jsonify(application_data)

@app.route("/application/<int:application_id>", methods=["POST"])
def update_application(application_id):
    updatedApplication = GenerationRequestDb(id=application_id, **request.form)
    user = UserDb.query.first()
    try:
        db.session.merge(updatedApplication)
        db.session.commit()
        application = GenerationRequestDb.query.get(updatedApplication.id)
        application_dir = os.path.join(
                    APPLICATIONS_DIR, str(user.id), str(application.id)
        )
        position_data = {
            "recruiters": application.recruiters
        }
        process.export_cover_letter(
            details=user.to_dict()["details"], 
            position_data=position_data, 
            cover_letter_content=application.cover_letter,
            language=LANGUAGES[selected_language],
            application_folder=application_dir,
            output_type="svg"
        )
        return application_dir, 200
    except Exception as e: 
        return "Impossible to update application: ${e}", 400


@app.route("/download_application/<int:application_id>", methods=["GET"])
def download_application(application_id):
    try:
        user = UserDb.query.first()
        application = GenerationRequestDb.query.get(application_id)
        if not application:
            abort(404, description="Application not found")

        position_data = {
            "recruiters": application.recruiters
        }
        process.export_cover_letter(
            details=user.to_dict()["details"], 
            position_data=position_data, 
            cover_letter_content=application.cover_letter,
            language=LANGUAGES[selected_language],
            application_folder=APPLICATIONS_DIR,
            output_type="pdf"
        )
        file_path = os.path.join(APPLICATIONS_DIR, "cover_letter.pdf")

        if not os.path.exists(file_path):
            abort(404, description="File not found")

        return send_file(file_path, as_attachment=True), 200
    except Exception as e:
        print(f"Error: {e}")
        return "Impossible to update application: ${e}", 400


@app.route("/export_user", methods=["POST"])
def exportUser():
    print("Exporting user data...")
    user = UserDb.query.filter_by(id=1).first()  # TODO change to current user
    if user:
        return jsonify(user.to_dict())
    else:
        return "User not found", 404


if __name__ == "__main__":
    app.run(debug=False)
