# Study / AI

I built Study / AI as my final project for the Ironhack AI Engineering bootcamp. The idea came from something pretty simple: I can watch a YouTube tutorial, feel like I understand it, and then realize I can't explain half of it afterward. I wanted to make a tool that helps turn watching a video into actually learning from it.

The app works with one YouTube video at a time. You paste a link, let it process the video, and then you can ask questions about what you watched or test yourself with a quiz. I kept the interface clean because I wanted the video and the learning experience to be the main focus.

There are two main features: Ask AI and Quiz.

Ask AI is a chat connected to the video transcript. You can ask about a specific concept, request a simpler explanation, or continue with a follow-up question. The chat keeps the recent conversation in context, so you don't have to repeat everything in every message. When it finds a relevant moment in the video, it can also provide a timestamp that takes you back to that part. Being able to jump from an explanation to the original video was one of the details I especially wanted to get right. (Thanks to Felipe for the idea.)

The Quiz feature generates five questions from the video with a choice of easy, medium, or hard difficulty. You answer one question at a time, see whether you got it right, and get an explanation. At the end, you get your score. You can try again or choose a different level without processing the video all over again.

Behind the interface, I used Python and FastAPI for the backend and React with Vite for the frontend. To work with a video's content, the backend retrieves its transcript, splits it into smaller pieces, and keeps the timestamps attached to those pieces. I use OpenAI's text-embedding-3-small model to create embeddings and Pinecone to store and search them. Each video's data is separated so the assistant can focus on the video the user actually selected.

For the chat, I built a LangChain agent powered by GPT-4.1-mini. It has three tools, and each one has a different purpose. `search_current_video` finds transcript pieces that match a question. `get_current_video_context` retrieves the video's transcript in order when a wider explanation is needed. `find_video_moment` looks for a relevant moment and returns a YouTube link with a timestamp. The video ID is passed to these tools automatically, so the user can just ask questions normally.

I also added conversation history to make follow-up questions feel natural. The frontend sends recent messages together with the new question. This gives the agent context for messages like "Can you explain that more simply?" without pretending that it remembers conversations forever. The history belongs to the current chat session and isn't saved as permanent memory.

The Quiz uses the processed video content to generate questions at the selected difficulty. React handles the flow of questions, answer selection, feedback, and final score. I wanted both features to feel like parts of the same learning experience rather than two unrelated AI demos.

I deployed the frontend and backend separately on Vercel. The frontend is a React site, while the backend runs the FastAPI application and connects to OpenAI and Pinecone. The two communicate through API requests, with a Vercel rewrite forwarding requests from the website to the backend.

The live app is available at https://youtube-learning-frontend.vercel.app and the backend API documentation is at https://youtube-qa-chatbot.vercel.app/docs.

Building this was also a lesson in debugging. Something that worked locally didn't always work after deployment. I had to deal with missing Python dependencies in Vercel's build configuration and a difference in how Pinecone returned vector IDs. Fixing those issues made me understand the whole pipeline better, not just the individual pieces of code.

The biggest thing I learned is that building an AI app isn't just about calling a model. It's about getting data into the right shape, retrieving the right information, choosing when to use a tool, keeping the conversation useful, and making all of that work through a real interface.

Study / AI isn't supposed to replace the original video. I built it to help people spend less time passively watching and more time understanding, asking questions, and checking what they've learned.
