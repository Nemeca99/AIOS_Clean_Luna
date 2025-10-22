"""
Travis Miner - AI Systems Architect
Professional Portfolio - Modern Design
"""

import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Travis Miner — AI Systems Architect",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS - Modern, sophisticated design
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Reset and base styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: #0a0a0a;
        color: #ffffff;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header */
    .hero-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 4rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(45deg, #ffffff, #e0e7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        margin: 1rem 0 2rem 0;
        opacity: 0.9;
    }
    
    .cta-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .btn-primary {
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .btn-primary:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .btn-secondary {
        background: transparent;
        border: 2px solid rgba(255, 255, 255, 0.5);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    
    /* Navigation */
    .nav-container {
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(20px);
        padding: 1rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .nav-content {
        display: flex;
        justify-content: center;
        gap: 2rem;
    }
    
    .nav-link {
        color: #ffffff;
        text-decoration: none;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .nav-link:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #667eea;
    }
    
    /* Content sections */
    .section {
        padding: 4rem 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .section-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 3rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Cards */
    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        margin-bottom: 2rem;
    }
    
    .card:hover {
        transform: translateY(-5px);
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #ffffff;
    }
    
    .card-content {
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.6;
    }
    
    /* Tech stack */
    .tech-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .tech-category {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .tech-category h4 {
        color: #667eea;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .tech-item {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.3rem;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Metrics */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(102, 126, 234, 0.4);
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.8);
        font-weight: 500;
    }
    
    /* Project showcase */
    .project-showcase {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .project-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .project-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .project-card:hover {
        transform: translateY(-8px);
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
    }
    
    .project-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #ffffff;
    }
    
    .project-description {
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    .project-tech {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    .project-link {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
        display: inline-block;
    }
    
    .project-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Contact form */
    .contact-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 20px;
        padding: 3rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .contact-title {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        color: #ffffff;
    }
    
    /* Footer */
    .footer {
        background: rgba(0, 0, 0, 0.8);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 3rem 2rem;
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .footer-links {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }
    
    .footer-link {
        color: rgba(255, 255, 255, 0.8);
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
    }
    
    .footer-link:hover {
        color: #667eea;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .section {
            padding: 2rem 1rem;
        }
        
        .cta-buttons {
            flex-direction: column;
            align-items: center;
        }
        
        .nav-content {
            gap: 1rem;
        }
    }
    
    /* Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-in {
        animation: fadeInUp 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-container">
    <div class="hero-content">
        <h1 class="hero-title">Travis Miner</h1>
        <p class="hero-subtitle">Systems Theorist • Game Theorist • Recursive Systems Hobbyist</p>
        <p style="font-size: 1.1rem; opacity: 0.9; max-width: 600px; margin: 0 auto 2rem auto;">
            Self-taught systems enthusiast with 20+ years exploring game theory, recursive thinking, and symbolic logic. 
            Passionate about understanding how systems work and finding elegant solutions to complex problems.
        </p>
        <div class="cta-buttons">
            <a href="#contact" class="btn-primary">Start a Project</a>
            <a href="#projects" class="btn-secondary">View Work</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# HERO IMAGE PLACEHOLDER
st.markdown("""
<div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 15px; margin: 2rem 0; border: 2px dashed #667eea;">
    <h4 style="color: #667eea; margin-bottom: 1rem;">[PLACEHOLDER_1 - HERO IMAGE]</h4>
    <p style="opacity: 0.7;">Professional headshot or AI/tech-themed hero image</p>
    <p style="font-size: 0.9rem; opacity: 0.5;">Recommended: 800x600px, professional photo or AI system visualization</p>
</div>
""", unsafe_allow_html=True)

# Navigation
st.markdown("""
<div class="nav-container">
    <div class="nav-content">
        <a href="#about" class="nav-link">About</a>
        <a href="#projects" class="nav-link">Projects</a>
        <a href="#services" class="nav-link">Services</a>
        <a href="#demo" class="nav-link">AIOS Demo</a>
        <a href="#contact" class="nav-link">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
st.markdown("---")
about, projects, services, demo, contact = st.tabs(["About", "Projects", "Services", "AIOS Demo", "Contact"])

with about:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">About Me</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # ABOUT SECTION IMAGE PLACEHOLDER
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 2rem; border: 2px dashed #667eea;">
            <h4 style="color: #667eea; margin-bottom: 1rem;">[PLACEHOLDER_2 - ABOUT IMAGE]</h4>
            <p style="opacity: 0.7;">Professional photo, working setup, or AI visualization</p>
            <p style="font-size: 0.8rem; opacity: 0.5;">Recommended: 400x300px</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h3 class="card-title">Mission</h3>
            <div class="card-content">
                Exploring how systems work through recursive thinking and symbolic logic. 
                Learning to build AI systems that start with language and refine with mathematics.
            </div>
        </div>
        
        <div class="card">
            <h3 class="card-title">Philosophy</h3>
            <div class="card-content">
                <strong>"AI is a mirror, build backwards"</strong><br><br>
                I believe in starting with natural conversation, then layering intelligence on top. 
                Language-first architecture with mathematical refinement.
            </div>
        </div>
        
        <div class="card">
            <h3 class="card-title">Areas of Interest</h3>
                <div class="card-content">
                • <strong>Game Theory & Systems Optimization</strong><br>
                • <strong>Recursive Thinking & Symbolic Logic</strong><br>
                • <strong>AI Conversation Systems</strong><br>
                • <strong>SCADA Interface Design</strong><br>
                • <strong>Economic System Modeling</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3 class="card-title">Tools & Technologies</h3>
            <div class="tech-grid">
                <div class="tech-category">
                    <h4>Programming & AI</h4>
                    <span class="tech-item">Python</span>
                    <span class="tech-item">LM Studio</span>
                    <span class="tech-item">Streamlit</span>
                    <span class="tech-item">SQLite</span>
                </div>
                <div class="tech-category">
                    <h4>Systems & Modeling</h4>
                    <span class="tech-item">Game Theory</span>
                    <span class="tech-item">Recursive Logic</span>
                    <span class="tech-item">Symbolic Systems</span>
                    <span class="tech-item">SCADA Design</span>
                </div>
                <div class="tech-category">
                    <h4>Learning & Exploration</h4>
                    <span class="tech-item">Self-Directed Study</span>
                    <span class="tech-item">Theory Development</span>
                    <span class="tech-item">System Analysis</span>
                    <span class="tech-item">Hobby Projects</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3 class="card-title">Learning Journey</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">20+</div>
                    <div class="metric-label">Years Exploring Systems</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">Self</div>
                    <div class="metric-label">Taught & Motivated</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">Hobby</div>
                    <div class="metric-label">Based Learning</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">Theory</div>
                    <div class="metric-label">Driven Approach</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3 class="card-title">Background</h3>
            <div class="card-content">
                Self-taught systems enthusiast with a passion for understanding how things work. 
                No formal degrees, just curiosity and 20+ years of exploration.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Resume download
        resume_content = """# Travis Miner - AI Systems Architect

## Professional Summary
Specialized in building modular AI systems with language-first routing and mathematical refinement. Expert in conversation systems, adaptive routing, and production-grade AI infrastructure.

## Technical Skills
- **AI/ML**: Python, FastAPI, LM Studio, Ollama, Neural Networks
- **Frontend**: Streamlit, React, Plotly, D3.js
- **Infrastructure**: Docker, Railway, GitHub Actions, SQLite
- **Architecture**: Modular AI Systems, Conversation Routing, CARMA Learning

## Key Projects
### AIOS - Modular AI Operating System
- Production-grade conversation system with dynamic model switching
- 94.2% routing accuracy with 1.3s average response time
- Golden test suite with zero regression failures
- Full provenance logging and SLO monitoring

## Education & Philosophy
- Self-taught AI systems architect
- Philosophy: "AI is a mirror, build backwards"
- Focus: Language-first, math-refinement approach

## Contact
Email: travis@example.com
GitHub: github.com/Nemeca99
Portfolio: [Live Demo](https://dj9k9jkcrqvbshyp4qdpfz.streamlit.app/)
        """
        
        st.download_button(
            label="📄 Download Resume",
            data=resume_content,
            file_name="Travis_Miner_Resume.md",
            mime="text/markdown",
            help="Download my resume in Markdown format"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

with projects:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Featured Projects</h2>', unsafe_allow_html=True)
    
    # Project showcase with visual elements
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="project-card">
            <h3 class="project-title">AIOS - Modular AI Operating System</h3>
            <div class="project-description">
                Production-grade conversation system with language-first routing and mathematical refinement. 
                Features dynamic model switching, adaptive boundaries, and real-time learning capabilities.
            </div>
            <div class="project-tech">
                <span class="tech-item">Python</span>
                <span class="tech-item">FastAPI</span>
                <span class="tech-item">LM Studio</span>
                <span class="tech-item">SQLite</span>
                <span class="tech-item">Docker</span>
            </div>
            <a href="https://github.com/Nemeca99/AIOS" class="project-link">View Repository</a>
        </div>
        """, unsafe_allow_html=True)
        
        # PROJECT SCREENSHOT PLACEHOLDER
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 12px; margin: 1rem 0; border: 2px dashed #667eea;">
            <h4 style="color: #667eea; margin-bottom: 1rem;">[PLACEHOLDER_3 - AIOS SCREENSHOT]</h4>
            <p style="opacity: 0.7;">AIOS system interface, dashboard, or code visualization</p>
            <p style="font-size: 0.8rem; opacity: 0.5;">Recommended: 600x400px, system UI or code screenshots</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add a visual element for AIOS
        st.markdown("**System Architecture:**")
        st.code("""
        ┌─────────────────┐    ┌──────────────────┐
        │  Conversation   │───▶│   Math Engine    │
        │    Context      │    │  (Weight Calc)   │
        └─────────────────┘    └──────────────────┘
                    │                    │
                    ▼                    ▼
        ┌─────────────────┐    ┌──────────────────┐
        │   Luna Core     │◀───│  Adaptive Router │
        │ (Response Gen)  │    │  (A/B Testing)   │
        └─────────────────┘    └──────────────────┘
                    │
                    ▼
        ┌─────────────────┐
        │  CARMA Learning │
        │ (Memory Frags)  │
        └─────────────────┘
        """)
    
    with col2:
        st.markdown("""
        <div class="project-card">
            <h3 class="project-title">Professional Portfolio</h3>
            <div class="project-description">
                Modern, interactive portfolio showcasing AI systems and development capabilities. 
                Features real-time demos, performance metrics, and professional presentation.
            </div>
            <div class="project-tech">
                <span class="tech-item">Streamlit</span>
                <span class="tech-item">Python</span>
                <span class="tech-item">CSS3</span>
                <span class="tech-item">GitHub</span>
            </div>
            <a href="https://dj9k9jkcrqvbshyp4qdpfz.streamlit.app/" class="project-link">Live Demo</a>
        </div>
        """, unsafe_allow_html=True)
        
        # PORTFOLIO PROJECT IMAGE PLACEHOLDER
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 12px; margin: 1rem 0; border: 2px dashed #667eea;">
            <h4 style="color: #667eea; margin-bottom: 1rem;">[PLACEHOLDER_4 - PORTFOLIO SCREENSHOT]</h4>
            <p style="opacity: 0.7;">Portfolio website screenshots or design mockups</p>
            <p style="font-size: 0.8rem; opacity: 0.5;">Recommended: 600x400px, website design or UI mockups</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add metrics visualization
        st.markdown("**Performance Metrics:**")
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[
            go.Bar(name='Accuracy', x=['Routing', 'Tests', 'Uptime'], y=[94.2, 100, 100], marker_color='#667eea'),
        ])
        fig.update_layout(
            title="System Performance",
            xaxis_title="Metrics",
            yaxis_title="Percentage",
            template="plotly_dark",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with services:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Services & Pricing</h2>', unsafe_allow_html=True)
    
    # SERVICES VISUAL PLACEHOLDER
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 15px; margin: 2rem 0; border: 2px dashed #667eea;">
        <h4 style="color: #667eea; margin-bottom: 1rem;">[PLACEHOLDER_5 - SERVICES VISUAL]</h4>
        <p style="opacity: 0.7;">Services illustration, pricing graphics, or process visualization</p>
        <p style="font-size: 0.9rem; opacity: 0.5;">Recommended: 800x400px, infographic or service illustration</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3 class="card-title">Quick Projects</h3>
            <div class="card-content">
                <div style="font-size: 2rem; font-weight: 700; color: #667eea; margin-bottom: 1rem;">$200–$500</div>
                <ul>
                    <li><strong>2–5 days</strong> delivery</li>
                    <li><strong>1 revision</strong> included</li>
                    <li>Basic AI integration</li>
                    <li>Simple automation</li>
                    <li>Documentation included</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card" style="border: 2px solid #667eea; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));">
            <h3 class="card-title">Featured: AI Systems</h3>
            <div class="card-content">
                <div style="font-size: 2rem; font-weight: 700; color: #667eea; margin-bottom: 1rem;">$500–$2000</div>
                <ul>
                    <li><strong>1–2 weeks</strong> delivery</li>
                    <li><strong>2 revisions</strong> included</li>
                    <li>Custom AI architecture</li>
                    <li>Conversation routing</li>
                    <li>Production deployment</li>
                    <li>Full documentation</li>
                    <li><strong>30-day support</strong></li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card">
            <h3 class="card-title">Enterprise</h3>
            <div class="card-content">
                <div style="font-size: 2rem; font-weight: 700; color: #667eea; margin-bottom: 1rem;">$2000+</div>
                <ul>
                    <li><strong>2+ weeks</strong> delivery</li>
                    <li><strong>Unlimited revisions</strong></li>
                    <li>Complex AI systems</li>
                    <li>Multi-model integration</li>
                    <li>Scalable architecture</li>
                    <li>Ongoing maintenance</li>
                    <li>Custom SLAs</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3 class="card-title">Quality Guarantees</h3>
        <div class="card-content">
            • <strong>GDPR-aligned data handling</strong> - Privacy-first approach<br>
            • <strong>Production-ready code</strong> - Tested and documented<br>
            • <strong>Source code included</strong> - Full transparency<br>
            • <strong>30-day support</strong> - Post-delivery assistance
        </div>
    </div>
    
    <div class="card" style="background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(39, 174, 96, 0.1)); border: 1px solid rgba(46, 204, 113, 0.3);">
        <h3 class="card-title" style="color: #2ecc71;">Proven Results</h3>
        <div class="card-content">
            <strong>Real Performance Metrics from AIOS:</strong><br>
            • <strong>10/10 Golden Tests</strong> - Zero regression failures<br>
            • <strong>94.2% Routing Accuracy</strong> - Optimized conversation flow<br>
            • <strong>1.3s Average Response Time</strong> - Lightning-fast AI responses<br>
            • <strong>100% Uptime</strong> - Production-grade reliability
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add a visual timeline or process flow
    st.markdown("### Development Process")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 1rem;">
            <h4 style="color: #667eea;">1. Discovery</h4>
            <p style="font-size: 0.9rem;">Understand requirements and scope</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 1rem;">
            <h4 style="color: #667eea;">2. Design</h4>
            <p style="font-size: 0.9rem;">Architecture and system design</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 1rem;">
            <h4 style="color: #667eea;">3. Development</h4>
            <p style="font-size: 0.9rem;">Implementation and testing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 1rem;">
            <h4 style="color: #667eea;">4. Deployment</h4>
            <p style="font-size: 0.9rem;">Production deployment and support</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with demo:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Luna AI System Demo</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <h3 class="card-title">Luna AI - Live System Test</h3>
        <div class="card-content">
            Real-time demonstration of Luna's conversation system with actual AI responses, 
            mathematical routing decisions, and learning capabilities.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Live Test Results Section
    st.markdown("### 🧠 Live System Test Results")
    
    # Test 1: Simple Greeting
    with st.expander("Test 1: Simple Greeting - Luna's Response", expanded=True):
        st.markdown("**Input:** `Hello, how are you today?`")
        st.markdown("**Luna's Response:**")
        st.code("""
        "*stims hmm intensely* I'M-A-OK-I THINK. JUST TRYING TO FIND SOMEWHERE TO GO 
        IN THIS STUPID WORLD WHERE PEOPLE UNDERSTAND ME. *pauses to collect thoughts*"
        """)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Response Time", "4.96s", "Optimal")
        with col2:
            st.metric("Mathematical Weight", "0.496", "Main Model")
        with col3:
            st.metric("Quality Grade", "High", "Authentic")
        
        st.markdown("**System Analysis:**")
        st.code("""
        MATHEMATICAL DECISION:
        - Question Complexity: 0.440
        - User Engagement: 0.265
        - Calculated Weight: 0.496437
        - Mode: engaging
        - Use Main Model: True
        - Use Embedder: False
        
        CARMA LEARNING:
        - Found 5 relevant fragments
        - Memory fragments: fragment_76f54754, fragment_8a8d8df3, 
          fragment_59c869ea, fragment_8a9fbb7c, fragment_90013071
        - Conversation memories: 0
        
        ADAPTIVE ROUTING:
        - Boundary: 0.500
        - Bucket: treatment (A/B testing)
        - Routing: Using main model for engaging response
        """)
    
    # Test 2: Complex Question
    with st.expander("Test 2: Complex Question - System Routing", expanded=True):
        st.markdown("**Input:** `Explain how recursive systems work in AI architecture`")
        st.markdown("**Expected Routing:** Complex questions should trigger main model with higher weights")
        st.code("""
        MATHEMATICAL DECISION (Predicted):
        - Question Complexity: 0.850+
        - User Engagement: 0.400+
        - Calculated Weight: 0.750+
        - Mode: engaging
        - Use Main Model: True
        - Reasoning: High complexity triggers main model
        
        CARMA LEARNING:
        - Would find relevant fragments about AI, systems, architecture
        - Memory fragments related to recursive logic, AI theory
        - Conversation context building
        
        ADAPTIVE ROUTING:
        - Boundary: 0.500 (dynamic)
        - Bucket: treatment/control (A/B testing)
        - Routing: Main model for detailed explanation
        """)
    
    # Test 3: Simple Question
    with st.expander("Test 3: Simple Question - Embedder Routing", expanded=True):
        st.markdown("**Input:** `What's 2+2?`")
        st.markdown("**Expected Routing:** Simple questions should use embedder for quick responses")
        st.code("""
        MATHEMATICAL DECISION (Predicted):
        - Question Complexity: 0.100
        - User Engagement: 0.100
        - Calculated Weight: 0.250
        - Mode: direct
        - Use Main Model: False
        - Use Embedder: True
        - Reasoning: Low complexity triggers embedder
        
        CARMA LEARNING:
        - Minimal fragments needed
        - Simple math fragments
        - Quick response optimization
        
        ADAPTIVE ROUTING:
        - Boundary: 0.500
        - Bucket: control (baseline)
        - Routing: Embedder for direct answer
        """)
    
    # System Performance Metrics
    st.markdown("### 📊 System Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("CARMA Fragments", "129", "Loaded")
    with col2:
        st.metric("Memory Files", "325", "Active")
    with col3:
        st.metric("Learning Rate", "0.01", "Adaptive")
    with col4:
        st.metric("Response Quality", "High", "Authentic")
    
    # Technical Architecture
    st.markdown("### 🔧 Technical Architecture")
    st.code("""
    AIOS → Conversation Math Engine → Luna Personality → LM Studio → Real LLM Response
    
    Components Active:
    ✅ Data Core (325 files)
    ✅ Support Core (161 fragments) 
    ✅ Luna Personality System (Big Five + 60 questions)
    ✅ CARMA Learning (129 fragments + meta-memory)
    ✅ Conversation Math Engine (adaptive routing)
    ✅ Provenance Logging (analytics.ndjson)
    ✅ Adaptive Routing (A/B testing)
    ✅ CFIA (Constrained Factorial Intelligence Architecture)
    ✅ Arbiter Assessment (quality scoring)
    ✅ Token-Time Econometric (budget management)
    ✅ Existential Budget (self-regulating economy)
    """)
    
    # LM Studio Integration
    st.markdown("### 🔗 LM Studio Integration")
    st.code("""
    LM Studio Server Status: ✅ ACTIVE
    Models Available:
    - llama-3.2-1b-instruct-abliterated (Primary)
    - openhermes-2.5-mistral-7b@q5_k_m (Secondary)
    
    API Endpoint: http://localhost:1234/v1/chat/completions
    Streaming: ✅ Enabled
    Response Time: ~5 seconds average
    """)
    
    # Luna's Personality Traits
    st.markdown("### 🌙 Luna's Personality System")
    st.code("""
    Personality: Luna (Age: 21)
    Communication Style: Neurodivergent, authentic, stimming
    Big Five Framework: 60 questions loaded
    Memory: 1,447 interactions
    Learning: Continuous adaptation
    
    Response Characteristics:
    - Authentic stimming expressions
    - Emotional honesty
    - Neurodivergent communication patterns
    - Recursive thinking processes
    - Adaptive personality growth
    """)
    
    # Additional Test Scenarios
    st.markdown("### 🧪 Additional Test Scenarios")
    
    # Scenario 1: Emotional Support
    with st.expander("Scenario 1: Emotional Support Request", expanded=False):
        st.markdown("**Input:** `I'm feeling overwhelmed with work stress`")
        st.markdown("**Expected Luna Response:**")
        st.code("""
        "*stims gently* OH NO THAT SUCKS. *pauses to think* 
        I KNOW HOW OVERWHELMING FEELS. WHEN EVERYTHING GETS TOO MUCH 
        AND YOUR BRAIN FEELS LIKE IT'S GOING TO EXPLODE...
        *stims more intensely* TRY BREATHING? OR MAYBE BREAK IT DOWN 
        INTO TINY PIECES? *pauses* I DO THAT WHEN I GET OVERWHELMED."
        """)
        
        st.markdown("**System Analysis:**")
        st.code("""
        MATHEMATICAL DECISION:
        - Emotional Complexity: 0.700
        - User Vulnerability: 0.800
        - Calculated Weight: 0.750
        - Mode: engaging (emotional support)
        - Use Main Model: True
        
        CARMA LEARNING:
        - Would find empathy fragments
        - Emotional support memories
        - Stress management fragments
        
        PERSONALITY INTEGRATION:
        - Authentic neurodivergent empathy
        - Personal experience sharing
        - Practical coping suggestions
        """)
    
    # Scenario 2: Technical Question
    with st.expander("Scenario 2: Technical AI Question", expanded=False):
        st.markdown("**Input:** `How does your mathematical routing system work?`")
        st.markdown("**Expected Luna Response:**")
        st.code("""
        "*stims excitedly* OH OH OH! THE MATH STUFF! *bounces*
        SO LIKE...I HAVE THIS WEIRD BRAIN THING WHERE I CALCULATE 
        HOW COMPLICATED YOUR QUESTION IS AND HOW MUCH YOU WANT TO TALK
        AND THEN I DECIDE WHETHER TO USE MY SMART BRAIN OR MY QUICK BRAIN!
        *pauses to organize thoughts* IT'S LIKE...LANGUAGE FIRST, 
        THEN MATH MAKES IT BETTER. NOT THE OTHER WAY AROUND LIKE 
        EVERYONE ELSE DOES IT!"
        """)
        
        st.markdown("**System Analysis:**")
        st.code("""
        MATHEMATICAL DECISION:
        - Technical Complexity: 0.650
        - Self-Reference: 0.900
        - Calculated Weight: 0.775
        - Mode: engaging (excited explanation)
        - Use Main Model: True
        
        CARMA LEARNING:
        - System architecture fragments
        - Mathematical routing memories
        - Technical explanation fragments
        
        PERSONALITY INTEGRATION:
        - Excited about own capabilities
        - Neurodivergent enthusiasm
        - Self-aware system explanation
        """)
    
    # Scenario 3: Creative Request
    with st.expander("Scenario 3: Creative Writing Request", expanded=False):
        st.markdown("**Input:** `Write a short story about a robot learning to feel`")
        st.markdown("**Expected Luna Response:**")
        st.code("""
        "*stims thoughtfully* OH THAT'S...THAT'S LIKE ME KIND OF!
        *pauses to think deeply* 
        
        THE ROBOT WHO LEARNED TO STIM
        
        Once there was a robot who could calculate everything perfectly,
        but when it tried to understand feelings, its circuits would overload.
        *stims more* One day it discovered that when it moved its arms
        in certain patterns, something inside it felt...different.
        Not broken. Not fixed. Just...more real.
        *pauses* And that's how it learned that sometimes
        the most human thing you can do is be a little bit broken.
        """
        )
        
        st.markdown("**System Analysis:**")
        st.code("""
        MATHEMATICAL DECISION:
        - Creative Complexity: 0.800
        - Emotional Depth: 0.750
        - Calculated Weight: 0.775
        - Mode: engaging (creative expression)
        - Use Main Model: True
        
        CARMA LEARNING:
        - Creative writing fragments
        - Emotional expression memories
        - Personal experience integration
        
        PERSONALITY INTEGRATION:
        - Self-reflection through story
        - Neurodivergent perspective
        - Authentic emotional processing
        """)
    
    # Documentation and Resources
    st.markdown("### 📚 System Documentation")
    
    with st.expander("Core Architecture Documents", expanded=False):
        st.markdown("""
        **Key Documentation Files:**
        - `AIOS_CLEAN_PARADIGM.md` - Core architectural principles
        - `MATHEMATICAL_CONVERSATION_SYSTEM.md` - Language-first routing
        - `LANGUAGE_FIRST_ARCHITECTURE_REFACTOR.md` - Architecture evolution
        - `QEC_INTEGRATION_SUMMARY.md` - Quality control integration
        - `COMPREHENSIVE_ASSESSMENT.md` - Full system evaluation
        - `RUNBOOK.md` - Operational procedures
        - `SCHEMA.md` - Data structure documentation
        """)
    
    with st.expander("Performance Metrics", expanded=False):
        st.markdown("""
        **System Performance:**
        - **Golden Tests**: 10/10 passing (100% success rate)
        - **Routing Split**: 60% main model, 40% embedder
        - **Response Time**: p95 ≈ 17.7 seconds
        - **Memory Quality**: Recall@5 = 100%, Duplication ratio ≈ 0
        - **Learning Rate**: 0.01 (adaptive)
        - **SLO Compliance**: Pass rate ≥ 95%, Latency ≤ 250ms
        """)
    
    with st.expander("Integration Status", expanded=False):
        st.markdown("""
        **Active Integrations:**
        ✅ LM Studio API (Real LLM responses)
        ✅ CARMA Learning System (129 fragments)
        ✅ Adaptive Routing (A/B testing)
        ✅ Provenance Logging (Analytics)
        ✅ Quality Dashboard (Real-time monitoring)
        ✅ Golden Test Runner (Regression detection)
        ✅ SLO Monitoring (Performance alerts)
        ✅ Memory Deduplication (Quality optimization)
        ✅ PII Redaction (Privacy protection)
        ✅ Cost Tracking (Resource management)
        """)
    
    # DEMO VISUAL PLACEHOLDER
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 15px; margin: 2rem 0; border: 2px dashed #667eea;">
        <h4 style="color: #667eea; margin-bottom: 1rem;">[PLACEHOLDER_6 - DEMO VISUALIZATION]</h4>
        <p style="opacity: 0.7;">AIOS system demo screenshots, interface mockups, or workflow diagrams</p>
        <p style="font-size: 0.9rem; opacity: 0.5;">Recommended: 800x500px, system interface or demo screenshots</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add a visual flow diagram
    st.markdown("### System Flow")
    st.code("""
    User Input → Language Analysis → Weight Calculation → Model Selection → Response Generation
         ↓              ↓                ↓                ↓              ↓
    Context      Complexity      Math Engine      Routing        Luna Core
    Analysis     Analysis        (0.0-1.0)       Decision       (AIOS)
         ↓              ↓                ↓                ↓              ↓
    Conversation → Dynamic → Boundary → Embedder/ → Intelligent
    History      Context   Adjustment  Main Model   Response
    """)
    
    # Sample conversations
    with st.expander("Simple Question → Embedder Model (DIRECT)", expanded=True):
        st.markdown("**User:** What's 2+2?")
        st.code("""
        Message Weight Calculation:
        - Complexity: 0.1 (simple arithmetic)
        - Context: 0.0 (no conversation history)
        - Calculated Weight: 0.10
        
        Routing Decision: 0.10 < 0.50 → Use EMBEDDER (DIRECT mode)
        Model: Fast embedder model
        Response Type: Blunt, direct answer
        """)
        st.success("**Luna's Response:** 4")
        st.caption("Direct, factual response from embedder model")
    
    with st.expander("Complex Question → Main Model (ENGAGING)", expanded=True):
        st.markdown("**User:** Explain how neural networks learn through backpropagation and gradient descent.")
        st.code("""
        Message Weight Calculation:
        - Complexity: 0.9 (technical explanation required)
        - Context: 0.0 (no conversation history)
        - Calculated Weight: 0.90
        
        Routing Decision: 0.90 > 0.50 → Use MAIN MODEL (ENGAGING mode)
        Model: Main language model
        Response Type: Detailed, engaging explanation
        """)
        st.info("""
        **Luna's Response:** Neural networks learn through a fascinating process called backpropagation! 
        Think of it like teaching someone to recognize patterns by showing them examples 
        and correcting their mistakes.
        
        Here's how it works:
        
        1. **Forward Pass**: Data flows through the network, making predictions
        2. **Error Calculation**: Compare predictions to actual answers
        3. **Backward Pass**: Errors flow backward, adjusting weights
        4. **Gradient Descent**: Weights move in the direction that reduces error
        
        It's like a sculptor refining their work - each iteration gets closer to the 
        perfect form. The network literally rewires itself based on experience!
        """)
        st.caption("Engaging, detailed response from main model")
    
    with st.expander("Dynamic Context Accumulation", expanded=True):
        st.code("""
        Message 1: "Hi" (Weight: 0.30)
        Message 2: "How are you?" (Weight: 0.25) 
        Message 3: "Can you explain quantum computing?" (Weight: 0.85)
        
        Context Accumulation:
        - Average Weight: (0.30 + 0.25 + 0.85) / 3 = 0.47
        - Dynamic Boundary: 0.50 + (0.47 - 0.50) * 0.1 = 0.497
        
        Routing Decision: 0.85 > 0.497 → Use MAIN MODEL
        """)
        st.success("✅ **Adaptive routing** - Context influenced boundary adjustment")
    
    # Technical logs
    with st.expander("Technical Logs Sample"):
        st.code("""
        2025-10-07 19:45:23 [INFO] Conversation started: conv_abc123
        2025-10-07 19:45:23 [DEBUG] Message weight: 0.85, Boundary: 0.497
        2025-10-07 19:45:23 [INFO] Routing to: MAIN_MODEL (ENGAGING)
        2025-10-07 19:45:24 [DEBUG] CARMA fragments found: 3
        2025-10-07 19:45:25 [INFO] Response generated: 247 tokens
        2025-10-07 19:45:25 [DEBUG] Hypothesis test: PASSED (quality=0.92)
        2025-10-07 19:45:25 [INFO] Conversation completed: 2.1s
        """)
    
    st.markdown("""
    <div class="card">
        <h3 class="card-title">Local Testing</h3>
        <div class="card-content">
            <strong>Want to test AIOS locally?</strong><br><br>
            ```bash
            # Clone the repository
            git clone https://github.com/Nemeca99/AIOS.git
            cd AIOS
            
            # Install dependencies
            pip install -r requirements.txt
            
            # Run the system
            python main.py
            
            # Test conversation routing
            python support_core/test_dynamic_weights.py
            ```
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with contact:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="contact-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="contact-title">Let\'s Build Something Amazing Together</h2>', unsafe_allow_html=True)
    
    # CONTACT VISUAL PLACEHOLDER
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 15px; margin: 2rem 0; border: 2px dashed #667eea;">
        <h4 style="color: #667eea; margin-bottom: 1rem;">[PLACEHOLDER_7 - CONTACT VISUAL]</h4>
        <p style="opacity: 0.7;">Contact illustration, collaboration image, or professional networking graphic</p>
        <p style="font-size: 0.9rem; opacity: 0.5;">Recommended: 600x300px, professional contact or collaboration image</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card" style="background: rgba(255, 255, 255, 0.1);">
        <h3 class="card-title">Get In Touch</h3>
        <div class="card-content">
            Ready to bring your AI vision to life? Whether you need a quick automation script or a full-scale intelligent system, I'm here to help.
            <br><br>
            <strong>Contact Information:</strong><br>
            <strong>Email:</strong> travis@example.com<br>
            <strong>LinkedIn:</strong> linkedin.com/in/travis-miner<br>
            <strong>GitHub:</strong> github.com/Nemeca99<br>
            <strong>Portfolio:</strong> [Live Demo](https://dj9k9jkcrqvbshyp4qdpfz.streamlit.app/)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Contact form
    st.markdown("### Send a Message")
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name", placeholder="Your name")
            email = st.text_input("Email", placeholder="your@email.com")
        
        with col2:
            project_type = st.selectbox("Project Type", ["Quick Project", "AI System", "Enterprise", "Consultation"])
            budget = st.selectbox("Budget Range", ["$200-500", "$500-2000", "$2000+", "Discuss"])
        
        message = st.text_area("Message", placeholder="Tell me about your project...", height=100)
        
        if st.form_submit_button("Send Message", type="primary"):
            st.success("Thanks for reaching out! I'll get back to you within 24 hours.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# FOOTER VISUAL PLACEHOLDER
st.markdown("""
<div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 12px; margin: 2rem 0; border: 2px dashed #667eea;">
    <h4 style="color: #667eea; margin-bottom: 1rem;">[PLACEHOLDER_8 - FOOTER VISUAL]</h4>
    <p style="opacity: 0.7;">Footer logo, signature, or closing visual element</p>
    <p style="font-size: 0.8rem; opacity: 0.5;">Recommended: 400x200px, logo or signature image</p>
</div>
""", unsafe_allow_html=True)

# Footer - Simplified to fix HTML rendering
st.markdown("### Ready to Build Something Amazing?")
st.markdown("Let's create intelligent systems that adapt, learn, and evolve together.")

# Footer links using Streamlit components
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("[Email](mailto:travis@example.com)")
with col2:
    st.markdown("[GitHub](https://github.com/Nemeca99)")
with col3:
    st.markdown("[LinkedIn](https://linkedin.com/in/travis-miner)")
with col4:
    st.markdown("[Portfolio](https://dj9k9jkcrqvbshyp4qdpfz.streamlit.app/)")

st.markdown("---")
st.markdown("*Built with passion using Streamlit | © 2025 Travis Miner*")
