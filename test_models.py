from app import app
from app.models import User, Subject, Chapter, Quiz, Question, Score
from app.extensions import db
import datetime

def test_model_relationships():
    with app.app_context():
        # Create test data
        try:
            # Create a test user
            test_user = User.query.filter_by(email="testuser@example.com").first()
            if not test_user:
                test_user = User(
                    email="testuser@example.com",
                    full_name="Test User",
                    qualification="Test Qualification"
                )
                test_user.set_password("testpass")
                db.session.add(test_user)
                db.session.commit()
                print("Created test user")
                
            # Create a test subject
            test_subject = Subject.query.filter_by(name="Test Subject").first()
            if not test_subject:
                test_subject = Subject(
                    name="Test Subject",
                    description="Test subject description"
                )
                db.session.add(test_subject)
                db.session.commit()
                print("Created test subject")
                
            # Create a test chapter
            test_chapter = Chapter.query.filter_by(name="Test Chapter").first()
            if not test_chapter:
                test_chapter = Chapter(
                    name="Test Chapter",
                    description="Test chapter description",
                    subject_id=test_subject.id
                )
                db.session.add(test_chapter)
                db.session.commit()
                print("Created test chapter")
                
            test_quiz = Quiz.query.filter_by(chapter_id=test_chapter.id).first()
            if not test_quiz:
                test_quiz = Quiz(
                    chapter_id=test_chapter.id,
                    date_of_quiz=datetime.datetime.now(),
                    time_duration=30,
                    remarks="Test quiz"
                )
                db.session.add(test_quiz)
                db.session.commit()
                print("Created test quiz")
                
            if Question.query.filter_by(quiz_id=test_quiz.id).count() == 0:
                for i in range(5):
                    question = Question(
                        quiz_id=test_quiz.id,
                        question_statement=f"Test question {i+1}?",
                        option1=f"Option 1 for question {i+1}",
                        option2=f"Option 2 for question {i+1}",
                        option3=f"Option 3 for question {i+1}",
                        option4=f"Option 4 for question {i+1}",
                        correct_option=1
                    )
                    db.session.add(question)
                db.session.commit()
                print("Created test questions")
                
            # Test relationships
            print("\nTesting relationships:")
            print(f"Subject {test_subject.name} has {len(test_subject.chapters)} chapters")
            print(f"Chapter {test_chapter.name} has {len(test_chapter.quizzes)} quizzes")
            print(f"Quiz id {test_quiz.id} has {len(test_quiz.questions)} questions")
            
            return True
            
        except Exception as e:
            print(f"Error testing models: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_model_relationships()
    if success:
        print("\nModel relationship test completed successfully!")
    else:
        print("\nModel relationship test failed!")