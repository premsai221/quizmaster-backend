import random
import datetime
from faker import Faker
from app import create_app
from app.models import User, Subject, Chapter, Quiz, Question, Score
from app.extensions import db

fake = Faker()

def seed_data():
    app = create_app()
    with app.app_context():
        # Clear existing data (optional)
        db.session.query(Score).delete()
        db.session.query(Question).delete()
        db.session.query(Quiz).delete()
        db.session.query(Chapter).delete()
        db.session.query(Subject).delete()
        db.session.query(User).filter(User.role != 'admin').delete()
        
        # Create test users
        print("Creating users...")
        users = []
        for i in range(10):
            user = User(
                email=fake.email(),
                full_name=fake.name(),
                qualification=random.choice(['High School', 'Bachelor', 'Master', 'PhD']),
                dob=fake.date_of_birth(minimum_age=18, maximum_age=60)
            )
            user.set_password('password123')
            db.session.add(user)
            users.append(user)
        
        # Create subjects
        print("Creating subjects...")
        subjects = []
        for i in range(5):
            subject = Subject(
                name=fake.unique.word() + " " + random.choice(['Science', 'Arts', 'Engineering', 'Mathematics']),
                description=fake.paragraph()
            )
            db.session.add(subject)
            subjects.append(subject)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create chapters for each subject
        print("Creating chapters...")
        chapters = []
        for subject in subjects:
            for i in range(random.randint(3, 6)):
                chapter = Chapter(
                    name=f"Chapter {i+1}: {fake.unique.word().title()}",
                    description=fake.paragraph(),
                    subject_id=subject.id
                )
                db.session.add(chapter)
                chapters.append(chapter)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create one quiz per chapter
        print("Creating quizzes...")
        quizzes = []
        start_date = datetime.datetime.now() + datetime.timedelta(days=7)
        for chapter in chapters:
            quiz_date = start_date + datetime.timedelta(days=random.randint(0, 30))
            quiz = Quiz(
                chapter_id=chapter.id,
                date_of_quiz=quiz_date,
                time_duration=random.choice([30, 45, 60, 90]),
                remarks=fake.sentence()
            )
            db.session.add(quiz)
            quizzes.append(quiz)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create questions for each quiz
        print("Creating quiz questions...")
        for quiz in quizzes:
            question_count = random.randint(5, 15)
            for i in range(question_count):
                options = [fake.sentence() for _ in range(4)]
                question = Question(
                    quiz_id=quiz.id,
                    question_statement=fake.sentence() + "?",
                    option1=options[0],
                    option2=options[1],
                    option3=options[2],
                    option4=options[3],
                    correct_option=random.randint(1, 4)
                )
                db.session.add(question)
        
        # Create scores for some completed quizzes
        print("Creating scores...")
        past_quizzes = []
        past_date = datetime.datetime.now() - datetime.timedelta(days=30)
        # Create some quizzes in the past for scoring
        for i in range(15):
            chapter = random.choice(chapters)
            quiz_date = past_date + datetime.timedelta(days=random.randint(0, 25))
            quiz = Quiz(
                chapter_id=chapter.id,
                date_of_quiz=quiz_date,
                time_duration=random.choice([30, 45, 60, 90]),
                remarks=fake.sentence()
            )
            db.session.add(quiz)
            past_quizzes.append(quiz)
            
        db.session.commit()
        
        # Add questions to past quizzes
        for quiz in past_quizzes:
            question_count = random.randint(5, 15)
            for i in range(question_count):
                options = [fake.sentence() for _ in range(4)]
                question = Question(
                    quiz_id=quiz.id,
                    question_statement=fake.sentence() + "?",
                    option1=options[0],
                    option2=options[1],
                    option3=options[2],
                    option4=options[3],
                    correct_option=random.randint(1, 4)
                )
                db.session.add(question)
                
        db.session.commit()
        
        # Create scores for users
        for quiz in past_quizzes:
            # Get the number of questions for this quiz
            questions = Question.query.filter_by(quiz_id=quiz.id).all()
            total_questions = len(questions)
            
            # Create scores for random users
            for user in random.sample(users, random.randint(3, 7)):
                correct_answers = random.randint(0, total_questions)
                score = Score(
                    quiz_id=quiz.id,
                    user_id=user.id,
                    time_stamp_of_attempt=quiz.date_of_quiz + datetime.timedelta(hours=random.randint(1, 3)),
                    total_scored=correct_answers,
                    total_possible=total_questions,
                    completed=True
                )
                db.session.add(score)
        
        db.session.commit()
        print("Data gen complete!")

if __name__ == "__main__":
    seed_data()