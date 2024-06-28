# applai

ApplAI is a local webapp which allows you to generate a specific cover letter and curriculum vitae from an application URL and some personnal data

## SETUP
### Prerequisites
- `ollama`: models manager
- `typst`: template engine

#### AI Models
- `llama3:8b-instruct-q5_K_M`: main model
- `mistral:7b-instruct-q5_K_M`: alternative
- `gemma:2b-instruct-q2_K`: very fast, for testing only

#### Python dependencies
- `flask`
- `flask_sqlalchemy`
- `requests`
- `ollama`

### Run
- `cd src ; flask run`
- Go to http://127.0.0.1:5000 on your browser (only chrome-based are supported)

## ROADMAP
### WIP
- Import / export users data

### Issues
- Dynamics links not fully working with Firefox (ex: Links)
- Fix paths handling

### Alpha
- Docker
- Language/model selects width should be dynamic
- Application tiles smaller
- Extra inputs/textareas shall be invisible at start
- A section shall be invisible if empty (all sections appears if the mouse is over #user_data div)
- Hide import/export buttons while not hovering userdata section
- Application popup:
    - Fields on the left and preview on the right
    - Set max-size for the preview
- Footer with our names, copyrights, github link
- Buttons "delete", "run again" on the application (vertical dots menu selector aside close button)

### Beta
- Add CV support
- If the URL has yet been applied, propose to run a new generation (keep all versions)
- Optimize prompts & reduce calls
- Do not display "Work In Progress", it block the user from using the application. Instead, create an application tile with a loading status (so the user can add other applications to the queue)
- Cold boot on last state
- Application webpage
    - Lock cover letter modifications when the application is sent
    - Application status ["Not sent", "Pending", "In progress", "Game Over", "I GOT THE JOB"]

### V0
- Review [POST]/user API in order to better manage form save and database access
- Link skills to experiences/education
- Chrome extension
- Support external llm API
- Multi-profiles:
    - Popup with checkbox to pick data
    - Change borders of the picked items in the color of the profile
- Add a color to each profile (and use it on application's tiles borders)