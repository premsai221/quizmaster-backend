from celery import Celery
from flask import current_app
from app.extensions import db
from app.models import User, Quiz, Score
from datetime import datetime, timedelta
import csv
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

celery = Celery(__name__)

@celery.task
def send_daily_reminders():
    """
    Send daily reminders to users who haven't logged in or have new quizzes available
    """
    with current_app.app_context():
        # Find users who need reminders
        users = User.query.filter_by(role='user').all()
        
        # Find recent quizzes (created in the last 24 hours)
        recent_quizzes = Quiz.query.filter(
            Quiz.date_of_quiz >= datetime.utcnow() - timedelta(days=1)
        ).all()
        
        if recent_quizzes:
            for user in users:
                # Check if user has attempted these quizzes
                user_scores = Score.query.filter_by(user_id=user.id).all()
                attempted_quiz_ids = [score.quiz_id for score in user_scores]
                
                new_quizzes = [quiz for quiz in recent_quizzes if quiz.id not in attempted_quiz_ids]
                
                if new_quizzes:
                    # Send reminder email
                    send_email(
                        user.email,
                        "New Quizzes Available",
                        f"Hello {user.full_name},\n\nThere are {len(new_quizzes)} new quizzes available for you to attempt.\n\nRegards,\nQuiz Master Team"
                    )

@celery.task
def generate_monthly_report():
    """
    Generate and send monthly activity reports to all users
    """
    with current_app.app_context():
        # Get all users
        users = User.query.filter_by(role='user').all()
        
        # Current month
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        prev_month_start = datetime(prev_year, prev_month, 1)
        
        for user in users:
            # Get scores from the previous month
            scores = Score.query.filter(
                Score.user_id == user.id,
                Score.time_stamp_of_attempt >= prev_month_start,
                Score.time_stamp_of_attempt < month_start
            ).all()
            
            if scores:
                # Generate report
                total_quizzes = len(scores)
                avg_score = sum(score.total_scored for score in scores) / total_quizzes if total_quizzes > 0 else 0
                
                # Create HTML report
                html_report = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        h1 {{ color: #4a86e8; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h1>Monthly Activity Report</h1>
                    <p>Hello {user.full_name},</p>
                    <p>Here is your activity report for {prev_month}/{prev_year}:</p>
                    
                    <h2>Summary</h2>
                    <p>Total quizzes taken: {total_quizzes}</p>
                    <p>Average score: {avg_score:.2f}%</p>
                    
                    <h2>Details</h2>
                    <table>
                        <tr>
                            <th>Quiz ID</th>
                            <th>Date</th>
                            <th>Score</th>
                            <th>Total</th>
                            <th>Percentage</th>
                        </tr>
                """
                
                for score in scores:
                    percentage = (score.total_scored / score.total_possible * 100) if score.total_possible > 0 else 0
                    html_report += f"""
                        <tr>
                            <td>{score.quiz_id}</td>
                            <td>{score.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M')}</td>
                            <td>{score.total_scored}</td>
                            <td>{score.total_possible}</td>
                            <td>{percentage:.2f}%</td>
                        </tr>
                    """
                
                html_report += """
                    </table>
                    <p>Keep up the good work!</p>
                    <p>Regards,<br>Quiz Master Team</p>
                </body>
                </html>
                """
                
                # Send email with HTML report
                send_email(
                    user.email,
                    f"Monthly Activity Report - {prev_month}/{prev_year}",
                    "Please see the attached HTML report.",
                    html_content=html_report
                )

@celery.task
def export_quiz_data(user_id=None):
    """
    Export quiz data to CSV
    If user_id is provided, export quizzes for that user
    Otherwise export all quizzes (admin view)
    """
    with current_app.app_context():
        output = io.StringIO()
        writer = csv.writer(output)
        
        if user_id:
            # User view - export their quiz attempts
            scores = Score.query.filter_by(user_id=user_id).all()
            
            # Write header
            writer.writerow(['Quiz ID', 'Date Attempted', 'Score', 'Total Possible', 'Percentage'])
            
            # Write data
            for score in scores:
                percentage = (score.total_scored / score.total_possible * 100) if score.total_possible > 0 else 0
                writer.writerow([
                    score.quiz_id,
                    score.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M'),
                    score.total_scored,
                    score.total_possible,
                    f"{percentage:.2f}%"
                ])
        else:
            # Admin view - export all users' performance
            users = User.query.filter_by(role='user').all()
            
            # Write header
            writer.writerow(['User ID', 'Email', 'Full Name', 'Quizzes Taken', 'Average Score'])
            
            # Write data
            for user in users:
                scores = Score.query.filter_by(user_id=user.id).all()
                quizzes_taken = len(scores)
                avg_score = sum(score.total_scored for score in scores) / quizzes_taken if quizzes_taken > 0 else 0
                writer.writerow([
                    user.id,
                    user.email,
                    user.full_name,
                    quizzes_taken,
                    f"{avg_score:.2f}%"
                ])
        
        # Get the CSV data
        csv_data = output.getvalue()
        output.close()
        
        return csv_data

def send_email(to, subject, body, html_content=None):
    """Helper function to send emails"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = to
    
    part1 = MIMEText(body, 'plain')
    msg.attach(part1)
    
    if html_content:
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
    
    try:
        server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
        server.starttls()
        server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False