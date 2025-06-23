import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# API Keys Configuration - Use environment variables for security
OPENAI_API_KEY = "sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
SERPER_API_KEY = "3f056fb1XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Set environment variables
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["SERPER_API_KEY"] = SERPER_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM with error handling
try:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7
    )
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    st.error("Failed to initialize AI model. Please check your API configuration.")

# Initialize Search Tool
try:
    search_tool = SerperDevTool()
except Exception as e:
    logger.error(f"Failed to initialize search tool: {e}")
    search_tool = None

# Agent definitions remain the same...
dietary_planner = Agent(
    role="Dietary Planner",
    goal="Create personalized dietary plans based on user input and health goals",
    backstory="""You are an expert nutritionist and dietary planner with years of experience 
    in creating customized meal plans. You understand the science of nutrition, macronutrients, 
    and how different dietary approaches work for various fitness goals.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool] if search_tool else [],
    llm=llm
)

fitness_trainer = Agent(
    role="Fitness Trainer",
    goal="Generate customized workout routines based on fitness goals and user capabilities",
    backstory="""You are a certified personal trainer and fitness expert with extensive knowledge 
    in exercise science, workout programming, and injury prevention. You specialize in creating 
    effective workout plans for people of all fitness levels.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool] if search_tool else [],
    llm=llm
)

team_lead = Agent(
    role="Health & Wellness Coordinator",
    goal="Combine diet and workout plans into a comprehensive health strategy",
    backstory="""You are a holistic health coach who specializes in integrating nutrition and 
    fitness plans. You understand how diet and exercise work together synergistically to achieve 
    optimal health outcomes and can provide motivational guidance.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)


# Task creation functions remain the same...
def create_dietary_task(age, weight, height, activity_level, dietary_preference, fitness_goal):
    return Task(
        description=f"""Create a comprehensive personalized meal plan for a {age}-year-old person, 
        weighing {weight}kg, {height}cm tall, with an activity level of '{activity_level}', 
        following a '{dietary_preference}' diet, aiming to achieve '{fitness_goal}'.

        Your meal plan should include:
        - Breakfast, lunch, dinner, and snacks
        - Nutritional breakdown including macronutrients and vitamins
        - Proper hydration and electrolyte balance recommendations
        - Meal preparation tips for easy implementation
        - Caloric requirements based on their profile

        If you need additional nutritional information, use the search tool to find current dietary guidelines.""",
        agent=dietary_planner,
        expected_output="A detailed meal plan with nutritional breakdowns, meal timing, and preparation tips"
    )


def create_fitness_task(age, weight, height, activity_level, fitness_goal):
    return Task(
        description=f"""Generate a comprehensive workout plan for a {age}-year-old person, 
        weighing {weight}kg, {height}cm tall, with an activity level of '{activity_level}', 
        aiming to achieve '{fitness_goal}'.

        Your workout plan should include:
        - Warm-up routines (5-10 minutes)
        - Main exercises targeting the fitness goal
        - Cool-down and stretching routines
        - Exercise modifications for different fitness levels
        - Safety tips and injury prevention advice
        - Progress tracking methods
        - Weekly schedule recommendations

        If you need current exercise research or techniques, use the search tool to find updated information.""",
        agent=fitness_trainer,
        expected_output="A complete workout routine with exercises, sets, reps, and safety guidelines"
    )


def create_integration_task(name, age, weight, height, activity_level, dietary_preference, fitness_goal):
    return Task(
        description=f"""Create a holistic health strategy for {name}, integrating both the meal plan 
        and workout plan provided by the dietary planner and fitness trainer.

        User Profile:
        - Name: {name}
        - Age: {age} years
        - Weight: {weight}kg
        - Height: {height}cm
        - Activity Level: {activity_level}
        - Dietary Preference: {dietary_preference}
        - Fitness Goal: {fitness_goal}

        Your integration should include:
        - A personalized greeting for {name}
        - How the diet and exercise plans work together synergistically
        - Timeline and scheduling recommendations
        - Lifestyle tips for motivation and consistency
        - Progress tracking and plan adjustment guidance
        - Weekly structure combining both plans
        - Use tables where possible for better organization

        Present everything in a well-structured, motivational, and actionable format.""",
        agent=team_lead,
        expected_output="A comprehensive, integrated health strategy with clear guidelines and motivation",
        context=[create_dietary_task(age, weight, height, activity_level, dietary_preference, fitness_goal),
                 create_fitness_task(age, weight, height, activity_level, fitness_goal)]
    )


def get_full_health_plan(name, age, weight, height, activity_level, dietary_preference, fitness_goal):
    try:
        dietary_task = create_dietary_task(age, weight, height, activity_level, dietary_preference, fitness_goal)
        fitness_task = create_fitness_task(age, weight, height, activity_level, fitness_goal)
        integration_task = create_integration_task(name, age, weight, height, activity_level, dietary_preference,
                                                   fitness_goal)

        health_crew = Crew(
            agents=[dietary_planner, fitness_trainer, team_lead],
            tasks=[dietary_task, fitness_task, integration_task],
            process=Process.sequential,
            verbose=True
        )

        result = health_crew.kickoff()
        return result
    except Exception as e:
        logger.error(f"Error generating health plan: {e}")
        return f"Error generating plan: {str(e)}"


# Set up Streamlit UI with professional theme
st.set_page_config(
    page_title="AI Health & Fitness Planner",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling with eye-friendly colors
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&display=swap');

        /* Global Styles */
        .main {
            background-color: #F8F9FA;
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background-color: #F8F9FA;
        }

        /* Header Styles */
        .main-header {
            background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
            padding: 2.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(46, 134, 171, 0.15);
        }

        .main-title {
            color: white;
            font-size: 2.8rem;
            font-weight: 700;
            font-family: 'Inter', sans-serif;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .main-subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.2rem;
            font-weight: 400;
            margin-bottom: 0;
        }

        /* Sidebar Styles */
        .css-1d391kg {
            background-color: #FFFFFF;
            border-right: 1px solid #E9ECEF;
        }

        .sidebar-header {
            color: #2C3E50;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 1.3rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #2E86AB;
        }

        .sidebar-subheader {
            color: #6C757D;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 1rem;
            margin-bottom: 1rem;
        }

        /* Card Styles */
        .info-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            margin: 1.5rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border: 1px solid #E9ECEF;
        }

        .profile-card {
            background: linear-gradient(135deg, #2E86AB, #3B94BB);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin: 1.5rem 0;
            box-shadow: 0 4px 20px rgba(46, 134, 171, 0.2);
        }

        .profile-card h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            margin-bottom: 1rem;
            font-size: 1.4rem;
        }

        .results-card {
            background: white;
            border-radius: 12px;
            padding: 2.5rem;
            margin: 2rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #E9ECEF;
        }

        .results-header {
            color: #2E86AB;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .motivation-card {
            background: linear-gradient(135deg, #F18F01, #FF6B35);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin: 2rem 0;
            text-align: center;
            box-shadow: 0 4px 20px rgba(241, 143, 1, 0.2);
        }

        .motivation-card h4 {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 1.4rem;
            margin-bottom: 1rem;
        }

        /* Input Styles */
        .stSelectbox > div > div {
            background-color: white;
            border: 2px solid #E9ECEF;
            border-radius: 8px;
            transition: all 0.2s ease;
        }

        .stSelectbox > div > div:focus-within {
            border-color: #2E86AB;
            box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
        }

        .stNumberInput > div > div > input {
            background-color: white;
            border: 2px solid #E9ECEF;
            border-radius: 8px;
            transition: all 0.2s ease;
            font-size: 1rem;
        }

        .stNumberInput > div > div > input:focus {
            border-color: #2E86AB;
            box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
        }

        .stTextInput > div > div > input {
            background-color: white;
            border: 2px solid #E9ECEF;
            border-radius: 8px;
            transition: all 0.2s ease;
            font-size: 1rem;
        }

        .stTextInput > div > div > input:focus {
            border-color: #2E86AB;
            box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
        }

        /* Button Styles */
        .stButton > button {
            background: linear-gradient(135deg, #2E86AB, #A23B72);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(46, 134, 171, 0.2);
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(46, 134, 171, 0.3);
        }

        /* Alert Styles */
        .stAlert {
            border-radius: 8px;
            border: none;
        }

        .stSuccess {
            background-color: #D4F6D4;
            color: #155724;
            border-left: 4px solid #28A745;
        }

        .stError {
            background-color: #F8D7DA;
            color: #721C24;
            border-left: 4px solid #DC3545;
        }

        .stWarning {
            background-color: #FFF3CD;
            color: #856404;
            border-left: 4px solid #FFC107;
        }

        /* Spinner */
        .stSpinner {
            color: #2E86AB;
        }

        /* API Warning */
        .api-warning {
            background: linear-gradient(135deg, #FF6B35, #F18F01);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 2rem 0;
            text-align: center;
            box-shadow: 0 4px 20px rgba(255, 107, 53, 0.2);
        }

        .api-warning h4 {
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2.2rem;
            }

            .main-subtitle {
                font-size: 1rem;
            }

            .info-card, .results-card {
                padding: 1.5rem;
            }
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #F8F9FA;
        }

        ::-webkit-scrollbar-thumb {
            background: #2E86AB;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #A23B72;
        }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
    <div class="main-header">
        <h1 class="main-title">💪 AI Health & Fitness Planner</h1>
        <p class="main-subtitle">Professional AI-powered nutrition and fitness planning for your health goals</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.markdown('<h2 class="sidebar-header">⚙️ Configuration</h2>', unsafe_allow_html=True)
st.sidebar.markdown('<p class="sidebar-subheader">Customize your health plan</p>', unsafe_allow_html=True)

# User inputs with validation
age = st.sidebar.number_input("Age (years)", min_value=10, max_value=100, value=25, help="Enter your current age")
weight = st.sidebar.number_input("Weight (kg)", min_value=30, max_value=200, value=70, help="Enter your current weight")
height = st.sidebar.number_input("Height (cm)", min_value=100, max_value=250, value=170, help="Enter your height")

activity_level = st.sidebar.selectbox(
    "Activity Level",
    ["Low", "Moderate", "High"],
    help="Low: Sedentary lifestyle, Moderate: Regular exercise, High: Very active"
)

dietary_preference = st.sidebar.selectbox(
    "Dietary Preference",
    ["Keto", "Vegetarian", "Low Carb", "Balanced"],
    help="Choose your preferred dietary approach"
)

fitness_goal = st.sidebar.selectbox(
    "Fitness Goal",
    ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility"],
    help="Select your primary fitness objective"
)

# Profile Card
st.markdown("""
    <div class="profile-card">
        <h3>👤 Personal Information</h3>
        <p>Enter your name below to personalize your health plan</p>
    </div>
""", unsafe_allow_html=True)

name = st.text_input("Full Name", value="John Doe", help="Enter your full name for personalization")

# Validation and Plan Generation
if st.sidebar.button("🚀 Generate My Health Plan", help="Click to create your personalized plan"):
    # Input validation
    if not name.strip():
        st.sidebar.warning("⚠️ Please enter your name")
    elif not all([age, weight, height]):
        st.sidebar.warning("⚠️ Please fill in all required fields")
    elif not OPENAI_API_KEY or not SERPER_API_KEY:
        st.sidebar.error("🔑 API keys not configured")
    else:
        with st.spinner("🔄 Generating your personalized health & fitness plan..."):
            try:
                full_health_plan = get_full_health_plan(
                    name, age, weight, height, activity_level, dietary_preference, fitness_goal
                )

                # Display Results
                st.markdown("""
                    <div class="results-card">
                        <h2 class="results-header">🎯 Your Personalized Health Plan</h2>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div class="results-card">
                        <div style="white-space: pre-wrap; font-family: 'Inter', sans-serif; line-height: 1.6; color: #2C3E50;">
                            {full_health_plan}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.success("✅ Your personalized health and fitness plan has been generated successfully!")

            except Exception as e:
                logger.error(f"Error during plan generation: {e}")
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("💡 Please check your API configuration and try again")

# Motivational Section
st.markdown("""
    <div class="motivation-card">
        <h4>🏆 Your Health Journey Starts Here!</h4>
        <p>Consistency and dedication are the keys to success. Every small step you take brings you closer to your goals. Stay focused, stay committed, and transform your life!</p>
    </div>
""", unsafe_allow_html=True)

# API Configuration Warning
if not OPENAI_API_KEY or not SERPER_API_KEY or OPENAI_API_KEY == "your-openai-api-key-here":
    st.markdown("""
        <div class="api-warning">
            <h4>🔧 Configuration Required</h4>
            <p>Please configure your OpenAI and SerperDev API keys in your environment variables or Streamlit secrets to use this application.</p>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6C757D; font-size: 0.9rem; margin-top: 2rem;">
        <p>Built with ❤️ using Streamlit & CrewAI | Professional AI Health & Fitness Planning</p>
    </div>
""", unsafe_allow_html=True)