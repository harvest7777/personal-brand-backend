from ast import List
from calendar import c
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langchain.schema import AIMessage, HumanMessage
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url: str = os.environ.get("SUPABASE_URL") or ""
key: str = os.environ.get("SUPABASE_KEY") or ""
supabase: Client = create_client(url, key)

llm = ChatOpenAI(model="gpt-4o-mini")

def call_model(state):
    response = llm.invoke(state["messages"])
    return {
        "messages": state["messages"] + [response]
    }

def is_valid_name(user_input: str) -> bool:
    """Check if the user's message is an answer to 'What is your full name?'"""
    response = llm.invoke([
        HumanMessage(content=f"""
        You are validating user input.

        The user was asked: "What is your full name?"

        Determine if their response below *answers that question* by providing a name 
        (e.g., "My name is John", "I'm Alice Smith", "Call me Peter", etc.).

        Respond with only 'yes' or 'no'.

        User response: "{user_input}"
        """)
    ])
    answer = response.content.strip().lower()  # type: ignore
    return answer == "yes"


def extract_name(user_input: str):
    """Extract the full name from the user's input"""
    response = llm.invoke([
        HumanMessage(content=f"""
        Extract the full name from the following text.
        Respond with only the full name and nothing else.

        Text: "{user_input}"
        """)
    ])

    extracted_name = response.content.strip()  # type: ignore
    return extracted_name

def parse_resume(resume_contents: str) -> list[str]:
    """
    Given a user's resume contents as raw text, return a prompt for an LLM that instructs it to parse 
    the resume into a flat list of factual statements ("facts") about the user. The LLM should not
    invent or infer, but should reconstruct the facts in a way that is suitable for semantic search 
    or vector embeddings. Each fact should be a single atomic statement and based strictly on information
    present in the original resume.
    """
    prompt = f"""
    You are an expert resume parser.

    You will receive the content of a user's resume (as plain text). 
    Your task is to extract ALL discrete, factual statements ("facts") about the user, listing each fact on its own line.
    Each fact should be self-contained, unambiguous, and include enough contextual information—such as role, technology, organization, dates, awards, outcomes, and numbers—so that it could semantically match common recruiter questions (such as "Tell me about a time you used Next.js", "Have you worked under pressure?", "What teamwork experience do you have?", "Did you use Python?", etc.).

    — Do NOT add, invent, or infer information not explicitly in the original resume text.
    — Do NOT summarize, generalize, or group facts; instead, list each as a stand-alone, atomic fact suitable for semantic search or question-answering.
    — Each fact should be a full, clear sentence that clearly attributes the experience, skill, or achievement to the user, and can be directly matched to a specific recruiter query about their work, technologies, team experience, pressure situations, awards, etc.
    — Include all critical context for each fact. If relevant, spell out the technologies, dates, role titles, organizations, outcomes, or details from the resume, so the fact is understandable and useful without needing to refer to the original text.
    — Rephrase and expand as needed only to maximize clarity and make each fact more likely to match a variety of recruiter questions.

    Output only the list of facts, with each fact on its own line.

    Resume:
    \"\"\"
    {resume_contents}
    \"\"\"
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return [fact.strip() for fact in response.content.strip().split("\n") if fact.strip() != ""] # type: ignore


if __name__ == "__main__":
    resume = """
    Ryan Tran
    Torrance, CA | ryan.tran7312@gmail.com | linkedin.com/in/ryan-p-tran | github.com/harvest7777
    Education
    California State University, Long Beach BS Computer Science - 4.0/4.0 GPA Expected May 2027
    Long Beach, CA
    Relevant Coursework: Data Structures & Algorithms, Object Oriented Programming, Databases, Operating Systems,
    Computer Architecture
    Skills
    AI/ML: AI Cloud Infrastructure, RAG, Embeddings, Vector Databases, OpenAI API, LangChain
    Languages: Python, C++, SQL, JavaScript, TypeScript, HTML/CSS
    Frameworks & Databases: React, Next.js, Flask, Express.js, MongoDB, PostgreSQL, Supabase, Upstash
    Developer Tools: Unix, Git, Docker, Google Cloud, AWS, Vercel, Ubuntu
    Experience
    Software Developer heavytomodified | NextJS, Supabase, Stripe, Git September 2025 - Current
    Remote
    • Architecting and implementing relational database schema to support white labeling of 100+ tenants
    • Migrating 200,000+ records of user data to new database schema
    Software Engineer Intern Fetch AI | Agents, AI, LLMs, Composio, Git September 2025 - Current
    Remote
    • Designing and implementing an AI agent for the Fall 2025 Cohort
    • Implemented agent-as-a-service architecture to support personalized agents of 20,000+ users
    Software Engineer Intern Bazalu | NextJS, React, MongoDB, OpenAI API, Git, Fastify May 2025 - August 2025
    Long Beach, CA
    • Integrated OpenAI text embedding with MongoDB to enable semantically relevant product searches
    • Designed and implemented REST APIs for customer facing website
    • Utilized static site generation and JSON LD to optimize SEO to improve search visibility of local businesses
    Web Developer & Mentor October 2024 - April 2025
    Association for Computing Machinery Club | React, Tailwind, Git Long Beach, CA
    • Created hackathon site resulting in 500+ applications and 10,000+ impressions using React and Tailwind
    • Mentored 100+ hackers to quickly solve merge conflicts and fix project configs
    Hackathons Wins
    1st Place – LAHacks | Agentic AI, LLM, React, Tailwind, Flask April 2025
    • Won $2,000 with a team of 3 against 1,000+ competitors at UCLA
    • Debugged through 5,000+ lines of AI generated code by applying fundamental knowledge in AI Agents, LLMs,
    Flask, and React
    1st Place - MarinaHacks | AWS, Docker, Socket.io, Express.js, HTML/CSS, Git October 2024
    • Won as a solo developer against 80+ other participants by developing a multiplayer browser game using Express.js,
    Socket.io, and HTML/CSS in 24 hours
    • Containerized app with Docker and deployed to an AWS EC2 box for demonstration
    Projects
    130+ Users - imalockin | NextJS, PostgreSQL, Supabase, Google OAuth, Git December 2024 - June 2025
    • Developed a full-stack social media platform with 2000+ hours of active use time
    • Ensured responsive design for 40% of the userbase of mobile users
    1,000+ Users - Binary Tree OSU | JavaScript, HTML/CSS April 2024
    • Used by 300+ students every semester, selected by CS professors to integrate into official Data Structures &
    Algorithms curriculum
    • Utilized HTML canvas with JavaScript and CSS to create a Binary Tree traversal game
    """
    facts = parse_resume(resume)
    print(facts)