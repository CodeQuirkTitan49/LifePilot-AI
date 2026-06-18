import streamlit as st
from PIL import Image
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json 
import sqlite3
import urllib.parse
from datetime import datetime, timedelta


load_dotenv() 

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")


conn = sqlite3.connect("lifepilot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT,
               summary TEXT,
               important_dates TEXT,
               status TEXT DEFAULT 'active')
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    task TEXT,
    completed INTEGER DEFAULT 0,
    FOREIGN KEY(document_id) REFERENCES documents(id)
)
""")

conn.commit()

st.set_page_config(
    page_title="LifePilot AI" , 
    page_icon="🚀"
)

st.title("🚀 LifePilot AI")
st.write("Your AI-powered life administration assistant.")


# SIDEBAR

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None

if st.sidebar.button("🏠 Home"):
    st.session_state.selected_document = None
    st.rerun()

st.sidebar.title("📂 My Documents")

# ACTIVE DOCUMENTS
cursor.execute("""
    SELECT id, title
    FROM documents
    WHERE status = 'active'
""")
saved_documents = cursor.fetchall()

st.sidebar.subheader("📌 Active")

for doc_id, title in saved_documents:
    if st.sidebar.button(
        title,
        key=f"doc_{doc_id}"
    ):
        st.session_state.selected_document = doc_id

# ARCHIVED DOCUMENTS
cursor.execute("""
    SELECT id, title
    FROM documents
    WHERE status = 'archived'
""")
archived_documents = cursor.fetchall()

st.sidebar.divider()
st.sidebar.subheader("📚 Archived")
if not archived_documents:
    st.sidebar.caption("No archived documents")
for doc_id, title in archived_documents:
    if st.sidebar.button(
        f"📚 {title}",
        key=f"archived_{doc_id}"
    ):
        st.session_state.selected_document = doc_id


if st.session_state.selected_document:
    cursor.execute("""
    SELECT title,
            summary,
            important_dates,
            status
    FROM documents
    WHERE id = ?
    """, (st.session_state.selected_document,))
    document = cursor.fetchone()

    if document is None:
        st.session_state.selected_document = None
        st.rerun()
    #display doc
    title, summary, important_dates, status = document
    
    if status == "archived":
        st.info("📚 Archived Document")
    else:
        st.success("📌 Active Document")

    st.subheader(f"📄 {title}")
    st.subheader("📝 Summary")
    st.write(summary)

    #display dates
    st.subheader("📅 Important Dates")
    dates = json.loads(important_dates)
    for index, item in enumerate(dates):
        st.write(
            f"{item['date']} - {item['event']}"
        )
        event_title = item["event"]

        try:
            event_date = datetime.strptime(
                item["date"],
                "%Y-%m-%d"
            )
            start_date = event_date.strftime("%Y%m%d")
            end_date = (
                event_date + timedelta(days=1)
            ).strftime("%Y%m%d")

            calendar_url = (
            "https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={urllib.parse.quote(event_title)}"
            f"&dates={start_date}/{end_date}"
            )

        except Exception as e:
            st.error(f"Date error: {e}")
            calendar_url = (
            "https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={urllib.parse.quote(event_title)}"
            )

        st.link_button (
            "📅 Add to Calendar",
            calendar_url
        )

    #load tasks
    cursor.execute("""
        SELECT id,
                task,
                completed
        FROM tasks
        WHERE document_id = ?
    """, (st.session_state.selected_document,))
    tasks = cursor.fetchall()

    #show tasks
    st.subheader("✅ Tasks")
    for task_id, task, completed in tasks:
        checked = st.checkbox(
            task,
            value=bool(completed),
            key=f"saved_{task_id}"
        )
        if checked != bool(completed):
            cursor.execute("""
                UPDATE tasks
                SET completed = ?
                WHERE id = ?
            """, (
                int(checked),
                task_id
            ))
            conn.commit()
            st.rerun()

    completed_count = sum(
        1 for _, _, completed in tasks if completed
    )
    total_tasks = len(tasks)
    if total_tasks > 0 :
        progress = completed_count/total_tasks
        st.subheader("📊 Progress")
        st.progress(progress)
        #f"{completed_count}/{total_tasks} tasks completed"
        st.metric(
            "Completion",
            f"{int(progress*100)}%"
        )

    if total_tasks > 0 and completed_count == total_tasks :
        st.success("🎉 All tasks completed!")
        if status == "active":
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📚 Archive Document"):

                    cursor.execute("""
                        UPDATE documents
                        SET status = 'archived'
                        WHERE id = ?
                    """, (
                        st.session_state.selected_document,
                    ))
                    conn.commit()
                    st.session_state.selected_document = None
                    st.rerun()

            with col2:
                if st.button("🗑 Delete Document"):

                    cursor.execute("""
                        DELETE FROM tasks
                        WHERE document_id = ?
                    """, (
                        st.session_state.selected_document,
                    ))

                    cursor.execute("""
                        DELETE FROM documents
                        WHERE id = ?
                    """, (
                        st.session_state.selected_document,
                    ))
                    conn.commit()
                    st.session_state.selected_document = None
                    st.rerun()
                
        elif status == "archived":
            st.info("📚 This document is archived.")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📤 Restore Document"):

                    cursor.execute("""
                        UPDATE documents
                        SET status = 'active'
                        WHERE id = ?
                    """, (
                        st.session_state.selected_document,
                    ))
                    conn.commit()
                    st.success("✅ Document restored!")
                    st.rerun()

            with col2:

                if st.button("🗑 Delete Document"):

                    cursor.execute("""
                        DELETE FROM tasks
                        WHERE document_id = ?
                    """, (
                        st.session_state.selected_document,
                    ))

                    cursor.execute("""
                        DELETE FROM documents
                        WHERE id = ?
                    """, (
                        st.session_state.selected_document,
                    ))
                    conn.commit()
                    st.session_state.selected_document = None
                    st.rerun()

def display_analysis(data, extracted_text):
    st.subheader("📄 Document Type")
    st.write(data["document_type"])

    st.subheader("📝 Summary")
    st.write(data["summary"])

    #imp dates
    st.subheader("📅 Important Dates")
    for item in data["important_dates"]:
        st.write(f"• {item['date']} — {item['event']}")

    # Suggested Actions (interactive)
    st.subheader("✅ Suggested Actions")

    for action in data["suggested_actions"]:
        st.write(f"• {action}")

    #future tracking
    st.subheader("📌 Future Tracking")
    st.write(
        "Would you like to save this document for future tracking?\n\n"
        "Saving allows you to resume progress later and track task completion."
    )

    col1, col2 = st.columns(2)

    with col1:
        save_track = st.button("💾 Save & Track")
    with col2:
        analyze_only = st.button("❌ Analyze Only")

    if analyze_only:
        st.info("Analysis completed. Nothing was saved.")

    if save_track:

        important_dates_json = json.dumps(
            data["important_dates"]
        )
        cursor.execute("""
            INSERT INTO documents (
            title,
            summary,
            important_dates           
            )
            VALUES(?,?,?)
        """, (
            data["document_type"],
            data["summary"],
            important_dates_json
        ))

        conn.commit()

        document_id = cursor.lastrowid

        for action in data["suggested_actions"]:

            cursor.execute("""
                INSERT INTO tasks (
                    document_id,
                    task,
                    completed
                )
                VALUES (?, ?, ?)
            """, (
                document_id,
                action,
                0
            ))

        conn.commit()
        st.success("✅ Saved to My Documents!")
        st.rerun()

    
    st.subheader("✉️ Response Required?")

    if data["response_required"]:
        st.success("Yes")
        st.write(data["response_reason"])

        if st.button("Generate Email Draft"):
            with st.spinner("Generating email draft..."):

                email_prompt = f"""
    Write a professional email.

    Purpose:
    {data["email_context"]}

    Based on this document:

    {extracted_text}
    """
                try:
                    email_response = model.generate_content(email_prompt)

                    st.subheader("📧 Email Draft")  
                    st.write(email_response.text)
                except Exception:
                    st.error("⚠ Email generation unavailable right now due to Gemini rate limits.")

    else:
        st.info("No response required.")

def parse_response(raw_response):
    cleaned_response = raw_response.strip()

    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response.replace(
            "```json",
            "",
            1
        )
    
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]

    cleaned_response = cleaned_response.strip()
    return json.loads(cleaned_response)

if st.session_state.selected_document is None:

    uploaded_file = st.file_uploader(
        "Upload a PDF or Image",
        type = ["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")

        if uploaded_file.type.startswith("image"):
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=350)

            with st.spinner("🤖 LifePilot is analyzing the image..."):
                image_prompt = """
                Analyze this document image.
                Return ONLY valid JSON.

                Use exactly this format:
                {
                    "document_type": "",
                    "summary": "",
                    "important_dates": [
                        {
                            "date": "2026-07-15",
                            "event": ""
                        } 
                    ],
                    "suggested_actions": [],
                    "response_required": false,
                    "response_reason": "",
                    "email_context": ""
                }

                IMPORTANT:
                Return all dates in YYYY-MM-DD format.
                """
                try:
                    response = model.generate_content(
                        [image_prompt, image]
                    )
                    raw_response = response.text
                except Exception:
                    st.error( "⚠ Unable to analyze image.")
                    st.stop()

                data = parse_response(raw_response)
                st.subheader("🧠 LifePilot Analysis")

                display_analysis(
                    data,
                    "Image Upload"
                )

        elif uploaded_file.type=="application/pdf":
            st.info("PDF uploaded successfully!")

            pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")

            extracted_text = ""

            for page in pdf:
                extracted_text += page.get_text()
            pdf.close()

            st.subheader("📄 Extracted Text")
            st.text_area(
                "PDF Content",
                extracted_text,
                height=300
            )

            if extracted_text.strip():
                with st.spinner("🤖 LifePilot is analyzing your document..."):

                    prompt = f"""
                    Analyze the following document.

                    Return ONLY valid JSON.
                    Do not include markdown.
                    Do not include explanations.
                    Do not wrap the JSON in triple backticks.

                    Determine whether the user is expected to send a response to this document.

                    Examples:
                    - Job interview invitation → true
                    - College application request → true
                    - Complaint requiring a reply → true
                    - Passport renewal notice → false
                    - Electricity bill → false
                    - Informational notice → false

                    Use exactly this JSON format:

                    {{
                        "document_type": "",
                        "summary": "",
                        "important_dates": [
                            {{
                                "date": "2026-07-15",
                                "event": ""
                            }}
                        ],
                        "suggested_actions": [],
                        "response_required": false,
                        "response_reason": "",
                        "email_context": ""
                    }}

                    Rules:
                    - Set response_required to true if the user is expected to reply.
                    - Explain why in response_reason.
                    - If response_required is true, briefly describe what the email should achieve in email_context.
                    - Otherwise, leave response_reason and email_context empty.

                    - IMPORTANT: Return ALL dates strictly in YYYY-MM-DD format.
                    - Example: 2026-07-15
                    - Do NOT use formats like:
                    - July 15, 2026
                    - 15 July 2026
                    - 15/07/2026

                    Document:
                    {extracted_text}
                    """
                    try: 
                        response = model.generate_content(prompt)
                        raw_response = response.text
                    except Exception:
                        st.error("⚠ Email generation unavailable right now due to Gemini rate limits.")
                        st.stop()

                    data = parse_response(raw_response)

                    st.subheader("🧠 LifePilot Analysis")

                    display_analysis(
                        data,
                        extracted_text
                    )


