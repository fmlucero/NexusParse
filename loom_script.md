# Loom Video Script: NexusParse (Job Application)

**Target length**: ~2.5 minutes (Maintain a steady, confident pace).
**Language**: English
**Objective**: Demonstrate that you have strong software engineering fundamentals, that you understand architecture/databases, and that you treat AI as an unreliable source that needs strict control (matching exactly what the job description asks for).

---

## 🎬 Screen Setup Before You Start
1. Have your **Visual Studio Code** open in the `NexusParse` project.
2. Open the **`docker-compose.yml`** file in one tab.
3. Open **`worker/tasks.py`** and **`worker/schemas.py`** in other tabs.
4. Keep your **terminal** open at the bottom, showing the successful `[+] Running 10/10` or a live `docker-compose logs` green output.
5. In the background, optionally have the architecture image (`nexusparse_architecture_concept.png`) open.

---

## 🗣️ The Script

### 1. Introduction (0:00 - 0:20)
**[Camera on you, screen showing the Architecture image or `docker-compose.yml`]**

"Hi everyone, I'm Facundo. I've been coding and shipping software long before AI tools existed, which means I treat AI as a force multiplier, not a crutch. Today, I want to walk you through **NexusParse**, a distributed, asynchronous AI extraction system I recently built."

### 2. The Problem & The Product (0:20 - 1:00)
**[Show the terminal with the Docker containers running]**

"The problem with extracting complex structured data using LLMs in production is twofold: First, LLMs are historically slow, which blocks traditional API gateways. Second, they hallucinate, which corrupts databases. 

So, rather than a monolithic script, I architected this as an event-driven fleet. I containerized a FastAPI gateway that handles JWT auth, stores the raw files safely in a MinIO bucket, and immediately publishes a message to a Redis queue, returning an HTTP 202 instantly to the client. This means the user never experiences timeouts."

### 3. The Core Technical Decision (1:00 - 2:00)
**[Switch to your IDE. Show `schemas.py` and then `tasks.py`]**

"The main technical decision I want to highlight is how I handled the unreliability of AI. 

I don't trust LLMs blindly. In `schemas.py`, I implemented hyper-strict validation using Pydantic. It doesn't just enforce data types; it enforces algorithmic integrity in real-time. For example, validating that the generated quantity multiplied by the unit price exactly matches the total price.

If the LLM hallucinates—which we know it will—the validation fails. But instead of crashing the system, I designed the Celery worker in `tasks.py` to intercept that generic `ValidationError` and trigger an **exponential retry backoff**. 

This creates a self-healing loop under the hood. The system forces the LLM to auto-correct itself in the background before any payload touches our PostgreSQL database. To support this at scale, I designed these Celery tasks to be strictly idempotent, and modeled the database to index deeply nested JSONB structures. I didn't want 'AI hype'; I wanted a resilient, observability-first data pipeline."

### 4. Why This Fits The Role (2:00 - 2:30)
**[Look directly at the camera / Loom circle]**

"I use AI every day to prototype faster and write boilerplate. But when a Celery worker gets stuck, a Docker network drops, or a database migration fails in production, AI can't fix it for you. You need solid fundamentals in observability, database modeling, and debugging to actually unblock the team.

I'm completely comfortable navigating existing codebases, making smart architectural modifications, and owning features end-to-end without needing my hand held. I love what you guys are building at your incubator, and I'd be ready to jump in and ship from day one. 

Thanks for your time!"

---

### 💡 Tips for the recording:
- **Don't sound robotic:** Speak natively. If you mess up a word, just keep going. They literally wrote *"This doesn't need to be polished"*.
- **Confidence:** They want someone who doesn't panic. Keep your tone calm and authoritative when explaining why LLMs shouldn't be trusted blindly.
- **Audio:** Make sure your mic is clear! Good audio makes you sound twice as professional.
