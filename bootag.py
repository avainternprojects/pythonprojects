import streamlit as st
import json
import random
import time
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Multi-Agent AI Tutor System",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state for persistent data
if 'learner_state' not in st.session_state:
    st.session_state.learner_state = {
        'concepts': {
            'Algebra': {'mastery': 0.3, 'attempts': 0, 'correct': 0, 'errors': [], 'consecutive_incorrect': 0},
            'Geometry': {'mastery': 0.5, 'attempts': 0, 'correct': 0, 'errors': [], 'consecutive_incorrect': 0},
            'Calculus': {'mastery': 0.2, 'attempts': 0, 'correct': 0, 'errors': [], 'consecutive_incorrect': 0},
            'Probability': {'mastery': 0.4, 'attempts': 0, 'correct': 0, 'errors': [], 'consecutive_incorrect': 0}
        },
        'session_history': [],
        'current_concept': None
    }

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'system_mode' not in st.session_state:
    st.session_state.system_mode = 'multi_agent'  # 'single_agent' or 'multi_agent'

# Sample questions database
QUESTIONS = {
    'Algebra': [
        {
            'question': 'Solve for x: 2x + 5 = 15',
            'answer': '5',
            'difficulty': 'easy',
            'explanation': 'Subtract 5 from both sides: 2x = 10, then divide by 2: x = 5'
        },
        {
            'question': 'Factor the expression: x² + 5x + 6',
            'answer': '(x+2)(x+3)',
            'difficulty': 'medium',
            'explanation': 'Find two numbers that multiply to 6 and add to 5: 2 and 3'
        }
    ],
    'Geometry': [
        {
            'question': 'What is the area of a circle with radius 5?',
            'answer': '78.54',
            'difficulty': 'easy',
            'explanation': 'Area = πr² = π × 25 ≈ 78.54'
        }
    ],
    'Calculus': [
        {
            'question': 'Find the derivative of f(x) = 3x² + 2x',
            'answer': '6x + 2',
            'difficulty': 'medium',
            'explanation': 'Use power rule: derivative of x² is 2x, derivative of x is 1'
        }
    ],
    'Probability': [
        {
            'question': 'What is the probability of rolling a 3 on a fair die?',
            'answer': '1/6',
            'difficulty': 'easy',
            'explanation': 'There is 1 favorable outcome out of 6 possible outcomes'
        }
    ]
}

# Agent implementations
class TeacherAgent:
    def __init__(self, mode='multi_agent'):
        self.mode = mode
    
    def generate_question(self, concept, difficulty=None):
        """Generate a question based on concept and learner state"""
        if concept not in QUESTIONS or not QUESTIONS[concept]:
            return None
        
        if difficulty:
            available = [q for q in QUESTIONS[concept] if q['difficulty'] == difficulty]
            if available:
                question = random.choice(available)
            else:
                question = random.choice(QUESTIONS[concept])
        else:
            question = random.choice(QUESTIONS[concept])
        
        return question
    
    def generate_explanation(self, question, learner_response):
        """Generate explanation based on learner response"""
        if learner_response.lower() == question['answer'].lower():
            return f"Correct! {question['explanation']}"
        else:
            return f"Your answer was incorrect. Here's the solution: {question['explanation']}"

class EvaluatorAgent:
    @staticmethod
    def assess_response(learner_response, correct_answer, concept):
        """Evaluate learner response and return assessment"""
        is_correct = str(learner_response).strip().lower() == str(correct_answer).strip().lower()
        error_type = None
        
        if not is_correct:
            # Simple error classification
            if any(op in learner_response for op in ['+', '-', '*', '/']):
                error_type = 'calculation_error'
            elif '=' in learner_response:
                error_type = 'equation_error'
            else:
                error_type = 'conceptual_error'
        
        return {
            'is_correct': is_correct,
            'error_type': error_type,
            'timestamp': datetime.now().isoformat()
        }

class KnowledgeGapAgent:
    @staticmethod
    def analyze_learner_state(learner_state):
        """Identify weak concepts based on learner state"""
        weak_concepts = []
        for concept, data in learner_state['concepts'].items():
            if data['mastery'] < 0.5:
                weak_concepts.append({
                    'concept': concept,
                    'mastery': data['mastery'],
                    'priority': 1 - data['mastery']  # Lower mastery = higher priority
                })
        
        # Sort by priority (most weak first)
        weak_concepts.sort(key=lambda x: x['priority'], reverse=True)
        return weak_concepts

class PedagogicalStrategyAgent:
    def __init__(self):
        self.strategy_policy = {
            'explanation': {'mastery_threshold': 0.3, 'error_type': 'conceptual_error'},
            'hint': {'mastery_threshold': 0.6, 'error_type': 'calculation_error'},
            'harder_question': {'mastery_threshold': 0.8, 'error_type': None}
        }
    
    def select_action(self, concept, learner_state):
        """Select teaching action based on formal policy"""
        concept_data = learner_state['concepts'][concept]
        mastery = concept_data['mastery']
        
        if mastery < 0.4:
            return 'explanation'
        elif mastery < 0.7:
            return 'hint'
        else:
            return 'harder_question'

# Main application
def main():
    # Title and header
    st.title("🎓 Multi-Agent AI Tutor System")
    st.markdown("---")
    
    # Sidebar for system controls
    with st.sidebar:
        st.header("System Configuration")
        
        # System mode selection
        mode = st.radio(
            "Select System Mode:",
            ["Multi-Agent System", "Single-Agent LLM Tutor"],
            index=0 if st.session_state.system_mode == 'multi_agent' else 1
        )
        
        if "Multi-Agent" in mode:
            st.session_state.system_mode = 'multi_agent'
            st.success("✅ Multi-Agent Mode Active")
        else:
            st.session_state.system_mode = 'single_agent'
            st.info("🤖 Single-Agent Mode Active")
        
        st.markdown("---")
        
        # Learner state visualization
        st.subheader("📊 Learner State Overview")
        
        # Create mastery chart
        concepts = list(st.session_state.learner_state['concepts'].keys())
        mastery_values = [st.session_state.learner_state['concepts'][c]['mastery'] for c in concepts]
        
        fig = go.Figure(data=[
            go.Bar(name='Mastery', x=concepts, y=mastery_values, marker_color='lightblue')
        ])
        fig.update_layout(
            title="Concept Mastery Levels",
            yaxis_title="Mastery (0-1)",
            yaxis_range=[0, 1],
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Knowledge gaps
        knowledge_gap_agent = KnowledgeGapAgent()
        weak_concepts = knowledge_gap_agent.analyze_learner_state(st.session_state.learner_state)
        
        if weak_concepts:
            st.warning("⚠️ Knowledge Gaps Detected")
            for gap in weak_concepts[:3]:  # Show top 3
                st.write(f"• {gap['concept']}: {gap['mastery']:.1%} mastery")
        
        st.markdown("---")
        
        # System reset
        if st.button("🔄 Reset Learner State"):
            for concept in st.session_state.learner_state['concepts']:
                st.session_state.learner_state['concepts'][concept] = {
                    'mastery': random.uniform(0.2, 0.5),
                    'attempts': 0,
                    'correct': 0,
                    'errors': [],
                    'consecutive_incorrect': 0
                }
            st.session_state.conversation_history = []
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Agent activity display
        st.subheader("🤖 Agent Activity Log")
        
        # Initialize agents
        teacher_agent = TeacherAgent(st.session_state.system_mode)
        evaluator_agent = EvaluatorAgent()
        strategy_agent = PedagogicalStrategyAgent()
        
        # Select concept
        selected_concept = st.selectbox(
            "📚 Select Learning Concept:",
            list(st.session_state.learner_state['concepts'].keys())
        )
        
        st.session_state.learner_state['current_concept'] = selected_concept
        
        # Display current concept mastery
        concept_data = st.session_state.learner_state['concepts'][selected_concept]
        mastery = concept_data['mastery']
        
        # Progress bar for mastery
        st.progress(mastery, text=f"Current Mastery: {mastery:.1%}")
        
        # Generate question button
        if st.button("🎯 Generate Practice Question", type="primary"):
            # Teacher Agent generates question
            difficulty = 'easy' if mastery < 0.5 else 'medium' if mastery < 0.8 else 'hard'
            question = teacher_agent.generate_question(selected_concept, difficulty)
            
            if question:
                st.session_state.current_question = question
                st.session_state.question_generated = True
                
                # Log agent activity
                timestamp = datetime.now().strftime("%H:%M:%S")
                activity = f"[{timestamp}] Teacher Agent: Generated '{difficulty}' question on {selected_concept}"
                st.session_state.conversation_history.append(activity)
                
                # Display question
                st.info(f"**Question:** {question['question']}")
                
                # Answer input
                user_answer = st.text_input("Your Answer:", key="answer_input")
                
                if st.button("📤 Submit Answer"):
                    if user_answer:
                        # Evaluator Agent assesses response
                        assessment = evaluator_agent.assess_response(
                            user_answer, 
                            question['answer'],
                            selected_concept
                        )
                        
                        # Update learner state
                        concept_data['attempts'] += 1
                        if assessment['is_correct']:
                            concept_data['correct'] += 1
                            concept_data['consecutive_incorrect'] = 0
                            st.success("✅ Correct!")
                        else:
                            concept_data['errors'].append(assessment['error_type'])
                            concept_data['consecutive_incorrect'] += 1
                            st.error("❌ Incorrect")
                        
                        # Update mastery (simple formula)
                        accuracy = concept_data['correct'] / concept_data['attempts'] if concept_data['attempts'] > 0 else 0
                        concept_data['mastery'] = 0.7 * concept_data['mastery'] + 0.3 * accuracy
                        concept_data['mastery'] = min(1.0, max(0.0, concept_data['mastery']))
                        
                        # Log evaluation
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        activity = f"[{timestamp}] Evaluator Agent: {'Correct' if assessment['is_correct'] else 'Incorrect'} - Error type: {assessment['error_type']}"
                        st.session_state.conversation_history.append(activity)
                        
                        # Pedagogical Strategy Agent selects action
                        if st.session_state.system_mode == 'multi_agent':
                            action = strategy_agent.select_action(selected_concept, st.session_state.learner_state)
                            
                            if action == 'explanation':
                                explanation = teacher_agent.generate_explanation(question, user_answer)
                                st.info(f"💡 **Explanation:** {explanation}")
                                activity = f"[{timestamp}] Pedagogical Agent: Provided explanation (strategy: {action})"
                                st.session_state.conversation_history.append(activity)
                            elif action == 'hint':
                                st.info(f"💡 **Hint:** {question['explanation'].split('.')[0]}")
                                activity = f"[{timestamp}] Pedagogical Agent: Provided hint (strategy: {action})"
                                st.session_state.conversation_history.append(activity)
                            else:
                                st.info("📈 **Next step:** Increasing difficulty for next question")
                                activity = f"[{timestamp}] Pedagogical Agent: Increasing difficulty (strategy: {action})"
                                st.session_state.conversation_history.append(activity)
                        
                        # Log in single-agent mode
                        else:
                            explanation = teacher_agent.generate_explanation(question, user_answer)
                            st.info(f"💬 **Feedback:** {explanation}")
                            activity = f"[{timestamp}] Single-Agent LLM: Provided feedback"
                            st.session_state.conversation_history.append(activity)
                        
                        # Knowledge Gap Agent analysis
                        if st.session_state.system_mode == 'multi_agent':
                            weak_concepts = knowledge_gap_agent.analyze_learner_state(st.session_state.learner_state)
                            if weak_concepts:
                                st.warning(f"📊 Knowledge Gap Agent: Weakest concept is {weak_concepts[0]['concept']} ({weak_concepts[0]['mastery']:.1%} mastery)")
                                activity = f"[{timestamp}] Knowledge Gap Agent: Identified {weak_concepts[0]['concept']} as weak concept"
                                st.session_state.conversation_history.append(activity)
                        
                        # Store session history
                        session_record = {
                            'timestamp': timestamp,
                            'concept': selected_concept,
                            'correct': assessment['is_correct'],
                            'mastery_before': mastery,
                            'mastery_after': concept_data['mastery']
                        }
                        st.session_state.learner_state['session_history'].append(session_record)
                        
                        st.rerun()
        
        # Display conversation history
        st.subheader("📝 Agent Interaction Log")
        history_container = st.container(height=300)
        with history_container:
            for entry in reversed(st.session_state.conversation_history[-10:]):  # Show last 10
                st.write(entry)
    
    with col2:
        # System architecture visualization
        st.subheader("🏗️ System Architecture")
        
        if st.session_state.system_mode == 'multi_agent':
            # Multi-agent architecture diagram
            st.markdown("""
            ```mermaid
            graph TD
                A[Teacher Agent] -->|Presents Question| C[Centralized Learner State]
                B[Student/Learner] -->|Responds| D[Evaluator Agent]
                D -->|Updates| C
                C -->|Reads| E[Knowledge Gap Agent]
                C -->|Reads| F[Pedagogical Strategy Agent]
                E -->|Identifies Weak Concepts| F
                F -->|Selects Action| A
            ```
            """)
            
            st.info("**Multi-Agent Features:**")
            st.write("• Explicit learner state")
            st.write("• Formal pedagogical policy")
            st.write("• Specialized agents")
            st.write("• Transparent decision logic")
        
        else:
            # Single-agent architecture
            st.markdown("""
            ```mermaid
            graph LR
                A[Single LLM Agent] -->|Question/Response| B[Student/Learner]
                B -->|Answer| A
                A -->|Implicit Adaptation| B
            ```
            """)
            
            st.warning("**Single-Agent Limitations:**")
            st.write("• Implicit learner modeling")
            st.write("• Reactive adaptation")
            st.write("• Limited transparency")
        
        # Show pedagogical strategy policy
        st.subheader("📋 Pedagogical Strategy Policy")
        
        policy_df = pd.DataFrame({
            'Learner State': ['Low mastery (< 0.4)', 'Medium mastery (0.4-0.7)', 'High mastery (> 0.7)'],
            'Action': ['Provide detailed explanation', 'Give hints', 'Increase difficulty'],
            'Condition': ['Conceptual errors', 'Calculation errors', 'Consistent success']
        })
        
        st.dataframe(policy_df, use_container_width=True, hide_index=True)
        
        # Performance metrics
        st.subheader("📈 Performance Metrics")
        
        if st.session_state.learner_state['session_history']:
            history = st.session_state.learner_state['session_history']
            if len(history) >= 2:
                accuracy = sum(1 for h in history if h['correct']) / len(history)
                mastery_gain = history[-1]['mastery_after'] - history[0]['mastery_before']
                
                col_metric1, col_metric2 = st.columns(2)
                with col_metric1:
                    st.metric("Session Accuracy", f"{accuracy:.1%}")
                with col_metric2:
                    st.metric("Mastery Gain", f"{mastery_gain:.3f}")
    
    # Footer with project info
    st.markdown("---")
    st.caption("""
    **Project:** Multi-Agent AI Tutor System with Explainable Learner State and Adaptive Strategy Policy  
    **Students:** Saranya Pothina, Pothireddy Divya Nagamani, Marasu Revanth, MD. Shakeer  
    **Guide:** Mrs. D. Kanakeswari, Ph.D | **Institution:** Baba Institute of Technology and Sciences
    """)

if __name__ == "__main__":
    main()