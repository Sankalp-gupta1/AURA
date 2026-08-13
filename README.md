# AURA – AI Personal Operating System

> Transforming fragmented digital information into actionable intelligence through AI-powered reasoning, memory, prioritization, planning, and decision support.

---

## Overview

Modern digital life is scattered across multiple platforms. Emails arrive continuously, meetings are scheduled across calendars, tasks remain hidden inside conversations, and important information gets buried under notifications.

As the volume of digital information increases, users spend more time searching, filtering, organizing, and remembering information rather than acting on it.

**AURA** is an AI-powered Personal Operating System designed to bridge this gap.

Instead of functioning as another productivity tool, AURA acts as an intelligent layer above existing digital systems. It collects, understands, remembers, prioritizes, plans, and presents information that truly requires attention.

With its latest architecture, AURA goes beyond simple information aggregation by introducing:

* Long-Term Memory
* AI Task Planning
* Multi-Agent Intelligence
* Action Proposals
* Human Approval Workflow
* Autonomous Task Execution
* Context-Aware AI Conversations

The goal is not simply to store information, but to convert information into intelligence and actionable decisions.

---

## Problem Statement

Professionals, students, researchers, and job seekers interact with dozens of digital systems every day.

Common challenges include:

* Important emails getting buried in crowded inboxes.
* Deadlines hidden inside conversations.
* Calendar events spread across multiple schedules.
* Action items manually tracked and often forgotten.
* Important personal information being repeatedly re-explained to AI systems.
* Information overload causing decision fatigue.
* Constant context switching between applications.
* AI assistants forgetting important user context between interactions.
* Users having to manually decide what action should be taken next.

Existing productivity tools help users organize information, but very few systems actively understand information, remember user context, create plans, and recommend actions.

As a result, users become managers of information rather than consumers of intelligence.

---

## Research Motivation

The rapid growth of AI has enabled machines to generate content, answer questions, and automate workflows. However, most AI systems remain reactive.

Users must explicitly ask questions before receiving assistance.

AURA explores a different direction:

> Can an AI system continuously understand a user's digital environment, remember important context, proactively identify priorities, create action plans, and recommend useful actions before the user even searches for them?

This project investigates how personal data sources such as emails, calendars, tasks, notes, and memories can be unified into a contextual reasoning layer capable of generating meaningful insights and recommendations.

---

## Proposed Solution

AURA introduces the concept of a **Personal Intelligence Layer**.

The system synchronizes information from multiple sources, analyzes contextual relationships, identifies priorities, extracts actionable tasks, remembers important user information, creates task plans, and delivers personalized briefings through an AI-driven interface.

Instead of asking users to continuously monitor multiple applications, AURA consolidates digital information into a single intelligent workspace.

The platform functions as a virtual **Chief of Staff** capable of understanding:

* Commitments
* Responsibilities
* Deadlines
* Opportunities
* Tasks
* Personal context
* User priorities
* Future actions

AURA can then transform this understanding into actionable recommendations while keeping the user in control of important actions.

---

## System Architecture

```text
┌─────────────────────────────────────────────┐
│                    USER                     │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│            AURA AI ORCHESTRATOR             │
│          Central Reasoning Layer            │
└──────────────────────┬──────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     Gmail Agent   Calendar Agent  Task Agent
          │            │            │
          └────────────┼────────────┘
                       ▼
┌─────────────────────────────────────────────┐
│          MEMORY & KNOWLEDGE LAYER           │
│                                             │
│  Long-Term Memory • Notes • User Context   │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│             AI PLANNING ENGINE              │
│                                             │
│     Reasoning • Prioritization • Planning  │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              ACTION SYSTEM                  │
│                                             │
│  Proposed → Approved/Rejected → Executed   │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│       PERSONALIZED INTELLIGENCE UI          │
│                                             │
│ Briefings • Memory • Tasks • Notes • AI    │
└─────────────────────────────────────────────┘
```

---

## Core Features

### Gmail Intelligence Engine

The Gmail Intelligence Engine analyzes synchronized emails and identifies important information that requires user attention.

Capabilities include:

* Security alert detection
* Job opportunity identification
* Deadline recognition
* Action item extraction
* Priority classification
* Email summarization
* Important email identification
* Context-aware email analysis

Instead of manually scanning hundreds of emails, users receive concise intelligence generated from their inbox.

---

### Calendar Awareness Engine

The Calendar Awareness Engine continuously tracks upcoming events and commitments.

Capabilities include:

* Upcoming meeting awareness
* Event tracking
* Schedule monitoring
* Priority event identification
* Daily planning support
* Calendar-aware task planning

The system maintains awareness of future obligations and integrates them into personalized recommendations.

---

### Automated Task Extraction

Many tasks remain hidden inside emails and conversations.

AURA can extract actionable information and convert it into structured task records.

Example:

```text
Input:

Complete IBM Coding Assessment before Sunday.
```

Generated Task:

```text
Priority: High
Task: Complete IBM Coding Assessment
Deadline: Sunday
```

This reduces manual effort while improving productivity.

---

### AI Task Planning

AURA now includes an AI-powered task planning system.

Instead of simply storing a task, AURA can analyze the task and generate a possible execution plan.

Example:

```text
Task:

Prepare AURA Project Demo
```

AURA may generate:

```text
Plan:

1. Prepare project overview
2. Test major features
3. Prepare demonstration flow
4. Review pending tasks
5. Prepare final presentation
```

This converts a simple task into an actionable workflow.

---

### Long-Term Memory

AURA now includes a persistent memory layer that allows the system to remember important user-provided information.

Users can explicitly teach AURA using the **Teach AURA** interface.

Example:

```text
My current project is AURA AI Assistant.
```

AURA can store this information as a long-term memory.

Example memory:

```text
FACT

My current project is AURA AI Assistant.
```

The memory system is designed to provide relevant context to the AI during future interactions.

This allows AURA to move from a stateless chatbot toward a more personalized AI system.

---

### Quick Notes

AURA includes a Quick Notes system for rapidly storing information.

Example:

```text
Remember to test the AURA memory system tomorrow.
```

Quick Notes provide a simple way to capture information without creating a complete task or long-term memory.

---

### Context-Aware AI Assistant

AURA's conversational AI can use synchronized information and relevant memory context while generating responses.

Example Questions:

```text
What are my important emails?

What should I focus on today?

Do I have any pending tasks?

What is my latest email?

Which upcoming event is most important?

What is my current project?

What important things do you remember about me?
```

The objective is to provide responses using user-specific context rather than generic answers.

---

### AI Briefing Engine

One of the most important components of AURA is its Briefing Engine.

The engine produces personalized summaries based on synchronized information, tasks, calendar events, priorities, and relevant context.

Example Output:

```text
Today's Focus

• IBM Coding Assessment pending
• Google Security Alert requires review
• Update TimesJobs profile
• 3 upcoming calendar events
• AURA project demo preparation
```

The objective is to provide clarity rather than notifications.

---

### Action Proposal System

AURA can convert AI-generated plans into proposed actions.

Instead of immediately executing important operations, AURA creates an action proposal.

Example:

```text
AI Plan
   ↓
Action Proposal
   ↓
User Review
   ↓
Approve / Reject
```

Possible actions can include:

* Create task
* Add subtask
* Create reminder
* Create calendar event
* Prepare email draft
* Update task status

This architecture provides a controlled bridge between AI reasoning and real-world actions.

---

### Human Approval Workflow

AURA follows a human-in-the-loop approach for important actions.

The basic workflow is:

```text
PROPOSED
    ↓
USER REVIEW
   ↙ ↘
REJECT  APPROVE
          ↓
       EXECUTE
```

This allows users to remain in control of actions suggested by the AI.

For example, if AURA proposes creating a calendar event, the user can review the action before approving it.

---

### Autonomous Executor

AURA includes an autonomous execution layer responsible for processing approved actions.

The executor receives approved actions and performs the corresponding operation through the appropriate service.

Conceptually:

```text
AI Reasoning
     ↓
Action Proposal
     ↓
Human Approval
     ↓
Autonomous Executor
     ↓
Service / Database
     ↓
Updated State
```

The system is designed around controlled autonomy rather than unrestricted automation.

---

## Multi-Agent Architecture

AURA uses an agent-oriented architecture where different components can specialize in different responsibilities.

Examples include:

```text
Gmail Agent
     ↓
Email Intelligence

Calendar Agent
     ↓
Schedule Intelligence

Task Agent
     ↓
Task Management

Memory System
     ↓
Long-Term Context

Task Strategist
     ↓
Planning & Reasoning

Autonomous Executor
     ↓
Approved Action Execution
```

This architecture allows AURA to scale toward a larger multi-agent Personal AI system.

---

## Technology Stack

### Frontend

* Next.js
* TypeScript
* Tailwind CSS
* React

### Backend

* FastAPI
* Python
* SQLAlchemy
* REST APIs

### AI Layer

* Gemini AI
* Prompt Engineering
* Context Aggregation
* AI Task Planning
* Agent-Based Reasoning

### Authentication

* Google OAuth 2.0

### Integrations

* Gmail API
* Google Calendar API

### Database

* SQLite
* SQLAlchemy ORM

### Architecture

* Modular Agent Architecture
* Service Layer
* API Layer
* Memory Layer
* Action Execution Layer

---

## Workflow

```text
User Login
      │
      ▼
Google OAuth Authentication
      │
      ▼
Email Synchronization
      │
      ▼
Calendar Synchronization
      │
      ▼
Task Extraction
      │
      ▼
Memory & Context Retrieval
      │
      ▼
AI Analysis
      │
      ▼
Task Planning
      │
      ▼
Action Proposal
      │
      ▼
User Approval
      │
      ▼
Action Execution
      │
      ▼
Dashboard Update
      │
      ▼
Conversational Intelligence
```

---

## Memory Workflow

```text
User
  │
  ▼
Teach AURA
  │
  ▼
Memory API
  │
  ▼
Memory Service
  │
  ▼
Database
  │
  ▼
Stored Memory
  │
  ▼
Relevant Context Retrieval
  │
  ▼
AI Assistant
```

---

## Action Workflow

```text
User Task
    │
    ▼
AURA AI Analysis
    │
    ▼
Task Planning
    │
    ▼
Action Proposal
    │
    ▼
┌───────────────┐
│ User Review   │
└───────┬───────┘
        │
   ┌────┴────┐
   ▼         ▼
REJECT     APPROVE
             │
             ▼
      Autonomous Executor
             │
             ▼
       Action Completed
```

---

## Key Contributions

* Designed and developed an AI-powered Personal Operating System.
* Integrated Gmail and Google Calendar into a unified intelligence platform.
* Developed automated task extraction and prioritization workflows.
* Built a contextual AI assistant capable of reasoning over personal data.
* Developed a persistent long-term memory architecture.
* Added a **Teach AURA** workflow for storing user-provided memories.
* Added Quick Notes for rapid information capture.
* Built AI-powered task planning and strategy generation.
* Developed an action proposal and approval workflow.
* Implemented a controlled autonomous execution layer.
* Introduced a modular agent-oriented architecture.
* Created an AI briefing engine for proactive decision support.
* Implemented secure OAuth-based authentication and data synchronization.

---

## Screenshots

### Dashboard

*Add dashboard screenshot here.*

---

### AI Briefing

*Add AI briefing screenshot here.*

---

### What AURA Remembers

*AURA's long-term memory interface allows users to view information remembered by the system.*

---

### Quick Notes

*Quick Notes provide a fast way to save information for AURA.*

---

### AI Task Planning

*AURA analyzes tasks and generates actionable plans.*

---

### Action Approval

*AURA presents proposed actions to the user before execution.*

---

### Gmail Intelligence

*Add Gmail intelligence screenshot here.*

---

### AURA Assistant

*Add AURA conversational assistant screenshot here.*

---

## Future Research Directions

Future versions of AURA will focus on expanding the platform into a more capable Personal AI Operating System.

Planned enhancements include:

* Advanced Long-Term Memory Architecture
* Memory Relevance and Retrieval
* Multi-Agent Collaboration Framework
* WhatsApp Integration
* LinkedIn Integration
* Voice-Based Interaction
* Personalized Recommendation Engine
* Advanced Autonomous Task Execution
* Meeting Scheduling Automation
* Cross-Platform Knowledge Graph
* Behavioral Learning Models
* Proactive Opportunity Detection
* Intelligent Workflow Automation
* Personalized Decision Support
* Cross-Application Agent Coordination

The long-term vision is to evolve AURA from an intelligent assistant into a proactive Personal AI system capable of understanding, remembering, planning, recommending, and safely executing tasks on behalf of users.

---

## Impact

AURA demonstrates how artificial intelligence can move beyond traditional chat interfaces and become an active participant in personal productivity and decision-making.

Rather than forcing users to manually manage fragmented information, AURA transforms digital signals into meaningful intelligence.

The combination of:

```text
Context
   +
Memory
   +
Reasoning
   +
Planning
   +
Human Approval
   +
Action Execution
```

creates a foundation for next-generation Personal AI Systems.

The project serves as an exploration of how AI can evolve from a reactive chatbot into a proactive intelligence layer that understands the user's digital environment and helps them decide what should happen next.

---

## Project Vision

The ultimate vision of AURA is:

> **"Don't just tell me what is happening. Understand it, remember what matters, help me decide what to do, and let me stay in control."**

AURA aims to become a Personal Operating System where information, memory, reasoning, planning, and action converge into a single intelligent environment.

---

## Author

### Sankalp Gupta

B.Tech Computer Science & Engineering

AI Engineer • Research Enthusiast • Intelligent Systems Builder

Focused on Human-Centered AI, Multi-Agent Systems, Productivity Intelligence, and Next-Generation Personal AI Platforms.

---

⭐ If you find this project interesting, consider giving it a star.
