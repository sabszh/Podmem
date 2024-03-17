# podmem▸

podmem▸ is a web application that generates flashcards from YouTube video transcripts. It allows users to convert educational content into easily digestible flashcards, enhancing learning and retention.

## Features
- **Automatic Flashcard Generation:** podmem▸ automatically parses the transcript of a YouTube video and generates flashcards based on the content.
- **Customizable Flashcards:** Users can customize the number of flashcards generated and adjust the difficulty level of the content.
- **Export Options:** Flashcards can be exported in various formats, including Anki, Brainscape, and Quizlet, for seamless integration with other study tools.

## Getting Started
To run podmem▸ locally on your machine:

1. Clone this repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Install a local MYSQL database **[here](https://dev.mysql.com/downloads/installer/)** 
4. Set up a .env file with the neccessary API keys from `config.py`
5. Run the Flask application in debug mode by executing `flask --app main run --debug`.
6. Access the application by navigating to `http://localhost:5000` in your web browser.

## Usage
1. Enter the URL of the YouTube video you want to generate flashcards from.
2. Adjust the amount and difficulty settings according to your preferences.
3. Click the "Generate Flashcards" button to generate flashcards from the video transcript.
4. View and interact with the generated flashcards on the podmem▸ interface.
5. Optionally, export the flashcards in your preferred format for use in other study tools.

## Data Handling and Privacy
Your privacy is important to us. podmem▸ handles all user data confidentially and anonymizes it for analysis purposes. Individual responses and personal information are not shared publicly or with third parties.

## Contact Information
For inquiries or feedback, please contact the developers via email at:
- Sabrina (szhsabrina@gmail.com)
- Gustav (gustav@movimentum.dk)

## Thank You
We appreciate your interest in podmem▸! Your valuable feedback and support drive our ongoing efforts to enhance and refine the application for the benefit of our users. If you'd like to contribute to the improvement of podmem▸, please consider participating in [this survey](https://forms.gle/MKXRmWMaAdmHKwyF8). Your input is invaluable to us!
