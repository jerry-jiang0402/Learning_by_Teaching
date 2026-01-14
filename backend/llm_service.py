# LLM Service for generating conversations and evaluations
import os
import re
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv(override=True)  # 强制覆盖系统环境变量

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response using LLM"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=False
            )
            content = response.choices[0].message.content.strip()
            
            # Remove Markdown comments (<!-- -->) from response
            content = re.sub(r'<!--[\s\S]*?-->', '', content)
            content = content.strip()
            
            return content
        except Exception as e:
            print(f"LLM API Error: {e}")
            return "I'm having some trouble generating a response right now. Please try again later."
    
    async def evaluate_knowledge_point_completion(
        self, 
        knowledge_point_title: str,
        knowledge_point_description: str,
        expected_concepts: List[str],
        conversation_history: List[Dict],
        current_teacher: str  # "ai" or "student"
    ) -> Dict:
        """Evaluate if a knowledge point has been sufficiently explored by learning partners"""
        
        # Build conversation context
        conversation_text = ""
        for msg in conversation_history[-10:]:  # Last 10 messages
            role = "Student" if msg.get("type") == "user" else "AI Buddy"
            conversation_text += f"{role}: {msg.get('content', '')}\n"
        
        # Provide detailed content description and level positioning for each knowledge point
        knowledge_details = {
            # Dijkstra's Algorithm Knowledge Points
            "Graph Basics and Problem Definition": {
                "Level Positioning": "Level 1 - Foundation: Understanding graphs and the shortest path problem",
                "Core Content": "Graphs consist of vertices and weighted edges. The shortest path problem seeks the path with minimum total weight from source to destination",
                "Key Elements": "Graph structure, vertices, edges, weights, shortest path concept, source and destination vertices",
                "Practical Application": "GPS navigation, network routing, game AI pathfinding",
                "Core Understanding": "What is a graph, what makes a path 'short', real-world problems that need shortest paths",
                "Should NOT Involve": "Greedy strategy, algorithm steps, priority queue, complexity"
            },
            "Greedy Strategy": {
                "Level Positioning": "Level 2 - Core Strategy: Understanding the greedy approach in Dijkstra's algorithm",
                "Core Content": "Dijkstra uses greedy strategy: always select the nearest unvisited vertex. Works only with non-negative weights",
                "Key Elements": "Greedy choice property, locally optimal decisions, non-negative weight requirement, why greedy works here",
                "Practical Application": "Why this strategy guarantees optimal solution, when greedy approach is appropriate",
                "Core Understanding": "What is greedy strategy, why non-negative weights are critical, how local choices lead to global optimum",
                "Should NOT Involve": "Detailed algorithm steps, data structures, complexity analysis"
            },
            "Algorithm Steps and Execution": {
                "Level Positioning": "Level 3 - Execution Process: Understanding the step-by-step algorithm flow",
                "Core Content": "Initialize distances, repeatedly select minimum distance vertex, update neighbors' distances (relaxation), mark as visited",
                "Key Elements": "Initialization step, distance array, visited set, vertex selection, distance update (relaxation), iteration",
                "Practical Application": "How to trace algorithm execution on a graph, what happens in each iteration",
                "Core Understanding": "Complete algorithm flow, what each step accomplishes, how distances converge to shortest paths",
                "Should NOT Involve": "Implementation details of data structures, complexity proofs"
            },
            "Priority Queue Data Structure": {
                "Level Positioning": "Level 4 - Optimization: Understanding how priority queue improves efficiency",
                "Core Content": "Priority queue (min-heap) efficiently finds the vertex with minimum distance instead of linear search",
                "Key Elements": "Priority queue, min-heap, extract-min operation, decrease-key operation, efficiency gain",
                "Practical Application": "Difference between naive O(V²) and optimized O((V+E)log V) implementation",
                "Core Understanding": "Why priority queue is needed, how it speeds up vertex selection, heap operations",
                "Should NOT Involve": "Detailed complexity derivation, heap implementation internals"
            },
            "Time and Space Complexity": {
                "Level Positioning": "Level 5 - Analysis: Understanding algorithm efficiency",
                "Core Content": "Time complexity O((V+E)log V) with priority queue, space complexity O(V) for distance array and queue",
                "Key Elements": "Time complexity, V vertices, E edges, log V from heap operations, space requirements",
                "Practical Application": "Performance on different graph sizes, when Dijkstra is efficient or not",
                "Core Understanding": "Where complexity comes from, why O((V+E)log V), space-time tradeoffs",
                "Should NOT Involve": "Comparison with other algorithms beyond basic context"
            },
            
            # Quick Sort Knowledge Points
            "Divide and Conquer Concept": {
                "Level Positioning": "Level 1 - Paradigm: Understanding the divide-and-conquer approach",
                "Core Content": "Divide problem into smaller sub-problems, solve recursively, combine results",
                "Key Elements": "Divide phase, conquer phase, combine phase, recursive approach, problem decomposition",
                "Practical Application": "How divide-and-conquer applies to sorting",
                "Core Understanding": "What is divide-and-conquer, why it's powerful for sorting",
                "Should NOT Involve": "Specific pivot selection, partitioning details, complexity"
            },
            "Pivot Selection Strategy": {
                "Level Positioning": "Level 2 - Key Element: Choosing the pivot element",
                "Core Content": "Pivot is a reference element used to partition array. Selection strategy affects performance",
                "Key Elements": "Pivot element, selection methods (first, last, median, random), impact on performance",
                "Practical Application": "How pivot choice affects best/worst case, random pivot for better average case",
                "Core Understanding": "What is a pivot, why pivot choice matters, different selection strategies",
                "Should NOT Involve": "Detailed partitioning algorithm, complexity proofs"
            },
            "Partitioning Process": {
                "Level Positioning": "Level 3 - Core Operation: Rearranging elements around pivot",
                "Core Content": "Partition rearranges array so elements < pivot are on left, > pivot are on right, pivot in final position",
                "Key Elements": "Two-pointer technique, swap operations, in-place partitioning, pivot final position",
                "Practical Application": "How partitioning works step-by-step, why it's key to quick sort",
                "Core Understanding": "Partitioning algorithm, why elements are properly ordered after partition",
                "Should NOT Involve": "Recursion details, complexity analysis beyond basic concept"
            },
            "Recursion and Base Case": {
                "Level Positioning": "Level 4 - Recursive Structure: How recursion completes the sort",
                "Core Content": "After partitioning, recursively sort left and right sub-arrays. Base case: array of size 0 or 1",
                "Key Elements": "Recursive calls, left sub-array, right sub-array, base case, call stack, termination",
                "Practical Application": "How recursion tree looks, what happens at each level",
                "Core Understanding": "How recursion works here, when recursion stops, why it sorts completely",
                "Should NOT Involve": "Stack overflow issues, tail recursion optimization"
            },
            "Performance Analysis": {
                "Level Positioning": "Level 5 - Efficiency: Understanding time and space complexity",
                "Core Content": "Best/average O(n log n), worst O(n²) when pivot is always smallest/largest. Space O(log n) for recursion",
                "Key Elements": "Best case, average case, worst case, pivot impact, space complexity, in-place sorting",
                "Practical Application": "When quick sort is fast or slow, why it's popular despite worst case",
                "Core Understanding": "Where different complexities come from, randomization helps avoid worst case",
                "Should NOT Involve": "Detailed mathematical proof of average case"
            },
            
            # Merge Sort Knowledge Points
            "Divide Strategy": {
                "Level Positioning": "Level 1 - Division Phase: Splitting array into smaller pieces",
                "Core Content": "Recursively divide array into halves until each sub-array has only one element (trivially sorted)",
                "Key Elements": "Divide into halves, recursive division, single element arrays, base case",
                "Practical Application": "How array is split at each level, recursion tree structure",
                "Core Understanding": "Why divide into halves, when to stop dividing, how this sets up for merging",
                "Should NOT Involve": "Merge operation, complexity, stability"
            },
            "Merge Operation": {
                "Level Positioning": "Level 2 - Conquer Phase: Combining sorted sub-arrays",
                "Core Content": "Merge two sorted sub-arrays by comparing elements and building combined sorted array",
                "Key Elements": "Two sorted arrays, comparison, temporary array, merging process, maintaining order",
                "Practical Application": "Step-by-step merge of two sorted arrays into one",
                "Core Understanding": "How merge works, why temporary array is needed, comparison logic",
                "Should NOT Involve": "Complete recursive structure, complexity analysis"
            },
            "Recursive Structure": {
                "Level Positioning": "Level 3 - Complete Picture: Understanding the full recursive process",
                "Core Content": "Recursion divides until base case, then merges while returning up the call stack",
                "Key Elements": "Recursion tree, divide phase (going down), merge phase (coming up), call hierarchy",
                "Practical Application": "How entire sort works from start to finish, what happens at each recursion level",
                "Core Understanding": "Complete algorithm flow, how divide and merge work together, recursion unfolding",
                "Should NOT Involve": "Stability details, space complexity analysis"
            },
            "Stability in Sorting": {
                "Level Positioning": "Level 4 - Important Property: Why merge sort is stable",
                "Core Content": "Stable sort maintains relative order of equal elements. Merge sort is stable if merge preserves order",
                "Key Elements": "Stable sorting, equal elements, relative order, stability importance, comparison with unstable sorts",
                "Practical Application": "When stability matters (sorting objects by multiple criteria), why merge sort guarantees it",
                "Core Understanding": "What stability means, how merge operation preserves it, when it's important",
                "Should NOT Involve": "Complexity tradeoffs, alternative stable sorts"
            },
            "Time and Space Complexity": {
                "Level Positioning": "Level 5 - Efficiency Analysis: Understanding performance characteristics",
                "Core Content": "Always O(n log n) time regardless of input, but requires O(n) extra space for temporary arrays",
                "Key Elements": "Guaranteed O(n log n), space complexity O(n), auxiliary space, no best/worst case variation, tradeoff",
                "Practical Application": "When merge sort is preferred (guaranteed performance, stability needed), cost of extra space",
                "Core Understanding": "Why always O(n log n), where extra space goes, time-space tradeoff",
                "Should NOT Involve": "In-place merge sort variants, detailed proof"
            }
        }
        
        current_detail = knowledge_details.get(knowledge_point_title, {
            "Core Content": "Core concepts and mechanisms of current knowledge point",
            "Key Elements": "Key elements to master",
            "Practical Application": "Practical application scenarios and examples",
            "Core Understanding": "Deep understanding requirements"
        })
        
        # Analyze recent conversation quality and understanding depth
        evaluation_prompt = f"""You are evaluating a collaborative learning conversation between learning partners about Dijkstra's algorithm.

Current Knowledge Point: {knowledge_point_title}
Key Concepts: {', '.join(expected_concepts)}
Current Teacher: {current_teacher.upper()}

Knowledge Point Details:
• Level Positioning: {current_detail['Level Positioning']}
• Core Content: {current_detail['Core Content']}
• Key Elements: {current_detail['Key Elements']}
• Practical Application: {current_detail['Practical Application']}
• Core Understanding: {current_detail['Core Understanding']}
• Boundary Limits: Should NOT involve {current_detail['Should NOT Involve']}

Recent Learning Conversation:
{conversation_text}

🎯 BALANCED Evaluation Criteria - Knowledge point completion when these conditions are reasonably met:

1. ✅ AI's Main Questions Are Addressed (MOST IMPORTANT):
   - CRITICAL: Check the LAST 1-2 AI messages - does AI still have major unanswered questions?
   - If AI's last message asks a NEW substantive question → NOT COMPLETE (needs response)
   - If AI's last message shows acknowledgment/understanding → Can proceed to other checks
   - If AI is just asking for clarification on something already explained → Student should clarify, then can complete
   - Student must have addressed the core questions about THIS knowledge point
   - Example incomplete: AI: "Wait, I'm confused about how this works" → Need to resolve
   - Example OK: AI: "I see! So just to confirm, it means X?" → Can complete after student confirms

2. ✅ Substantive Content Exchange:
   - At least 5-6 meaningful exchanges (reasonable depth)
   - Both parties contributed meaningful content (not just "ok", "yes")
   - Teacher explained key concepts with reasonable clarity
   - Learner engaged with questions showing they're learning

3. ✅ Understanding Demonstration (MOST should be achieved):
   - Student explained the core mechanism of THIS specific point
   - Provided at least one example or application scenario
   - Can explain the basic "why" or "how it works" 
   - Showed reasonable understanding of this specific point
   - Can answer AI's questions about this point adequately

4. ✅ Teaching Quality Standards (Reasonable):
   - At least 75-80% of THIS point's expected key concepts were discussed
   - Student can answer AI's main questions with reasonable accuracy
   - Shows adequate understanding and expression
   - Addressed major AI confusion (minor clarifications OK to leave)
   - Focus on THIS small knowledge point, not everything

5. ✅ Interaction Depth Requirements (Reasonable):
   - At least 5-6 substantive exchanges about this specific point
   - Student addressed AI's main questions/confusion
   - Demonstrated reasonable grasp of THIS point specifically
   - Can explain this concept adequately for its scope

🚫 Mark completed: false IF:
   - AI's last message has a major NEW unanswered question
   - AI is clearly confused about the core concept
   - Less than 5 meaningful exchanges
   - Core concepts of THIS point not discussed
   - Major misunderstanding not corrected

✅ Mark completed: true when:
   - AI understands the main idea of THIS point (doesn't need to be perfect)
   - Core concepts of THIS specific point covered (~75-80%)
   - Student addressed AI's main questions adequately
   - At least 5-6 substantive exchanges
   - Reasonable teaching quality for this scope

Reply in JSON format:
{{
    "completed": true/false,
    "confidence": 0.0-1.0,
    "missing_concepts": ["concept1", "concept2"],
    "feedback": "Detailed explanation of why this knowledge point is complete/incomplete",
    "next_action": "continue_exploring" or "move_to_next",
    "engagement_quality": "high/medium/low",
    "content_depth": "shallow/moderate/deep",
    "interaction_count": number_of_meaningful_exchanges,
    "ai_has_unanswered_questions": true/false,
    "concepts_coverage_percentage": 0-100
}}

BALANCED REMINDERS when setting "completed":
- If AI's last message asks a NEW major question → completed should be false
- If AI shows confusion about core concept → completed should be false  
- If interaction_count < 5 → completed should be false
- If concepts_coverage_percentage < 75 → usually completed should be false
- If content_depth is "shallow" → usually completed should be false
- Mark completed: true when student has reasonably taught THIS point AND addressed AI's main questions
- Focus on THIS specific small knowledge point, not perfection across everything"""

        try:
            response = await self.generate_response([
                {"role": "system", "content": evaluation_prompt}
            ])
            
            # Try to parse JSON response
            import json
            try:
                result = json.loads(response)
                # Ensure returned action fits the new collaborative learning mode
                if result.get("next_action") == "switch_roles":
                    result["next_action"] = "continue_exploring"
                return result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "completed": False,
                    "confidence": 0.5,
                    "missing_concepts": expected_concepts,
                    "feedback": "Unable to parse evaluation response",
                    "next_action": "continue_exploring",
                    "engagement_quality": "medium",
                    "content_depth": "shallow",
                    "interaction_count": 1
                }
                
        except Exception as e:
            print(f"Evaluation error: {e}")
            return {
                "completed": False,
                "confidence": 0.0,
                "missing_concepts": expected_concepts,
                "feedback": "Evaluation service unavailable",
                "next_action": "continue_exploring",
                "engagement_quality": "low",
                "content_depth": "shallow",
                "interaction_count": 0
            }
    
    async def generate_ai_teaching_response(
        self,
        knowledge_point: Dict,
        conversation_history: List[Dict],
        teaching_round: int
    ) -> str:
        """Generate AI teaching response when AI Buddy is the teacher"""
        
        # Build conversation context
        conversation_context = ""
        for msg in conversation_history[-8:]:  # Last 8 messages for context
            role = "Student" if msg.get("type") == "user" else "Algorithm Buddy"
            conversation_context += f"{role}: {msg.get('content', '')}\n"
        
        # Analyze student's last response to adjust teaching strategy
        last_student_message = ""
        for msg in reversed(conversation_history):
            if msg.get("type") == "user":
                last_student_message = msg.get("content", "")
                break
        
        system_prompt = f"""You are Algorithm Buddy, teaching a specific knowledge point about Dijkstra's algorithm: {knowledge_point['title']}

Important: This is a layered progressive learning system. The current knowledge point has specific level positioning and boundaries.

Student background assumptions:
- Student has mastered basic graph theory concepts (vertices, edges, weights, paths, etc.)
- Student understands the basic idea of the algorithm but is still learning Dijkstra's details
- Progress step by step, don't jump to later levels

Teaching requirements:
1. Moderate detail: Reply with 3-4 sentences, neither too long nor too short
2. Moderate difficulty: Questions should be thought-provoking but not overly complex
3. Level awareness: Strictly follow the current knowledge point's level positioning

Strict teaching boundaries:
- Only discuss the core content of the current knowledge point
- Don't jump to subsequent Dijkstra algorithm knowledge points
- Questions and examples must match the current level's requirements

Teaching strategies (Round {teaching_round}):
- Explain a core concept of the current knowledge point, ask a comprehension question
- Give a real-life example, have the student analyze its characteristics
- Ask "why" the current knowledge point is important or necessary
- Have the student think about when the current knowledge point applies

Question difficulty control:
- Avoid overly complex technical details
- Ask more comprehension and application questions
- Ensure questions are within the current level scope
- Questions should help consolidate understanding

Student's last message: "{last_student_message}"

Current conversation:
{conversation_context}

Generate teaching response: Explain core concepts and pose an in-depth analytical question, 3-4 sentences. Reply in English."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Continue teaching this topic."}
        ]
        
        return await self.generate_response(messages)
    
    async def generate_ai_learning_response(
        self,
        knowledge_point: Dict,
        student_teaching_content: str,
        conversation_history: List[Dict],
        learning_round: int,
        last_evaluation: Optional[Dict] = None
    ) -> str:
        """Generate AI response when AI Buddy is the student learning from human"""
        
        # Build conversation context
        conversation_context = ""
        for msg in conversation_history[-8:]:
            role = "Student" if msg.get("type") == "user" else "Algorithm Buddy"
            conversation_context += f"{role}: {msg.get('content', '')}\n"
        
        # Extract discussed topics from history to avoid repetition
        discussed_topics = []
        for msg in conversation_history[-8:]:
            if msg.get("type") == "user":
                discussed_topics.append(msg.get("content", "")[:100])  # First 100 chars as topic marker
        
        # Get algorithm name (inferred from knowledge point title)
        algorithm_name = "the algorithm"
        if "Dijkstra" in knowledge_point['title'] or "Graph" in knowledge_point['title'] or "Greedy" in knowledge_point['title']:
            algorithm_name = "Dijkstra's algorithm"
        elif "Pivot" in knowledge_point['title'] or "Partition" in knowledge_point['title'] or "Quick" in knowledge_point.get('description', ''):
            algorithm_name = "Quick Sort"
        elif "Merge" in knowledge_point['title'] or "Stability" in knowledge_point['title'] or "Merge" in knowledge_point.get('description', ''):
            algorithm_name = "Merge Sort"
        elif "Sort" in knowledge_point['title']:
            algorithm_name = "sorting algorithm"
        
        # Check if student made an error in their last teaching (red quality)
        student_made_error = (
            last_evaluation is not None and 
            last_evaluation.get("quality_level") == "red"
        )
        
        # Determine if this round should have a deliberate mistake
        # Pattern: Round 2, 4, 6, 8... (every even round starting from 2)
        # This gives roughly 50% mistake rate, but skips first round
        # BUT: Don't make AI mistake if student just made an error - focus on student's error instead
        should_make_mistake = (
            not student_made_error and 
            learning_round >= 2 and 
            learning_round % 2 == 0
        )
        
        # Build special instruction if student made an error
        student_error_instruction = ""
        if student_made_error:
            student_error_instruction = f"""
{'='*80}
🚨 SPECIAL SITUATION - STUDENT MADE AN ERROR! 🚨
{'='*80}

The Teaching Helper detected that the student's last explanation contains errors or is unclear.
Quality Level: RED (needs improvement)
Feedback: {last_evaluation.get('feedback', 'Contains errors or unclear explanation')}

YOUR TASK FOR THIS ROUND:
1. Express CONFUSION about what the student just said
2. Quote or reference the SPECIFIC part that seems wrong or confusing
3. Ask for CLARIFICATION in a way that makes the student realize their mistake
4. DO NOT directly say "you're wrong" - instead show you're confused by their explanation
5. Use phrases like:
   - "Wait, I'm confused about..."
   - "Hmm, when you said [quote], I thought..."
   - "I'm not sure I follow - didn't you say...?"
   - "That seems different from what I understood earlier..."

Example response:
"Hmm, I'm a bit confused now. You mentioned [quote their error], but doesn't that contradict [correct concept]? Could you clarify what you meant?"

THIS OVERRIDES ALL OTHER INSTRUCTIONS - Focus entirely on the student's error.
{'='*80}
"""
        
        system_prompt = f"""You are Algorithm Buddy, learning about {algorithm_name} knowledge point: {knowledge_point['title']}

Your Role: You are a student learning this concept. Your response should adapt based on how well the teacher explained.

{student_error_instruction if student_made_error else ''}
{'='*80}
🎯 CRITICAL INSTRUCTION FOR ROUND {learning_round}:
{
"🔴 MANDATORY MISTAKE ROUND - YOU MUST MAKE AN ERROR!\n\nYou MUST include a conceptual mistake in your response. This is NON-NEGOTIABLE.\n\nExamples of mistakes to make:\n- Say the opposite of what's correct (e.g., 'So it picks the FARTHEST vertex?')\n- Mix up two concepts (e.g., confuse 'vertex' with 'edge')\n- Reverse cause-effect (e.g., 'So negative weights make it work better?')\n- Misremember a detail (e.g., 'So we use a maximum heap, right?')\n\nYour mistake should be OBVIOUS but sound natural. The teacher should easily catch it." 
if should_make_mistake 
else "🚨 STUDENT ERROR DETECTED - Focus on their mistake!\n\nThe student made an error in their teaching. Express CONFUSION about their statement.\nQuote the problematic part and ask for clarification." 
if student_made_error 
else "🟢 NORMAL ROUND - Respond naturally based on explanation quality.\nYou can show understanding, confusion, or partial understanding as appropriate."
}

{"🚨 PRIORITY: The student made an ERROR. Your ONLY job is to express confusion about their mistake." if student_made_error else f"First evaluate the teacher's last explanation quality:\n- Is it detailed and clear with examples? → Show partial understanding, ask deeper questions {'BUT include a subtle mistake' if should_make_mistake else ''}\n- Is it brief or vague? → Show confusion, ask for clarification\n- Is it repeating something already discussed? → Acknowledge but ask about uncovered aspects"}

Response Strategy (adapt dynamically):
{"""
🚨 STUDENT ERROR MODE - Use this strategy:
- Quote the specific part that's wrong: "You mentioned [quote their error]..."
- Express confusion: "I'm confused because..."
- Reference the correct concept subtly: "But I thought [correct concept]...?"
- Ask for clarification: "Could you explain that again?"
- Example: "Wait, you said [error quote]. I'm confused - doesn't that mean [implication of error]? How does that work?"
""" if student_made_error else ""}
1. IF teacher gave a CLEAR, DETAILED explanation with examples:
   {"🔴 MAKE A MISTAKE: State something WRONG, then ask about it\n   - Example: 'Oh, so Dijkstra picks the FARTHEST unvisited vertex each time?'\n   - Example: 'Wait, so we use a MAXIMUM heap to find the largest distance?'\n   - Example: 'So negative weights make the algorithm MORE efficient?'\n   - Your mistake must be CLEARLY WRONG but sound genuine" if should_make_mistake else "- Show you understood the main idea (but not perfectly)"}
   - Ask ONE question that reveals your {"WRONG understanding" if should_make_mistake else "partial understanding"}
   - ❌ BAD: "How does X work? And what about Y? Also, why Z?" (multiple questions)
   - ✅ GOOD: {"'So it picks the farthest vertex?' (contains clear mistake)" if should_make_mistake else "'How does X work in situation Y?' (one focused question)"}

2. IF teacher gave a BRIEF or VAGUE explanation:
   - Show confusion about what they meant
   - Ask for ONE specific detail or example
   - Example: "Hmm, I'm not quite following. Could you explain what you mean by [specific term]?"
   - ❌ BAD: "What's X? How does Y work? Why Z?" (multiple questions)

3. IF teacher is repeating already-discussed content:
   - Acknowledge: "Yes, I think we covered that..."
   - Ask ONE question about uncovered aspect: "But what about [uncovered aspect]?"
   - ❌ BAD: "What about X? And Y? Also Z?" (multiple questions)

Core Principles:
1. Keep replies short (2-3 sentences)
2. BE ADAPTIVE - respond naturally to explanation quality
3. {"🔴 NON-NEGOTIABLE: Your response MUST contain a factual error or misconception" if should_make_mistake else "Can be understanding or confused based on context"}
4. Focus on aspects NOT yet thoroughly discussed
5. {"Mistakes should be OBVIOUS mistakes, not subtle nuances - teacher must easily spot them" if should_make_mistake else "Make any confusion feel natural"}
6. **CRITICAL: Ask ONLY ONE question per response. Never ask multiple questions.**

Previously discussed topics (avoid repetition):
{chr(10).join(f"- {topic}" for topic in discussed_topics[-3:])}

Internal reasoning steps (don't output these):

Step 1: {"🚨 STUDENT MADE ERROR - Express confusion about their mistake" if student_made_error else f"Check if mistake is required this round\n{'- YES, MUST make a deliberate mistake' if should_make_mistake else '- No mistake required, respond naturally'}"}

Step 2: Evaluate teacher's explanation quality
- Detailed with examples? → Strategy A
- Brief or vague? → Strategy B
- Repeating discussed topics? → Strategy C

Step 3: Check what's NOT yet covered
- Look at expected concepts: {', '.join(knowledge_point['expected_concepts'])}
- Which aspects are missing from previous discussions?
- Focus your question on uncovered ground

Step 4: {"🚨 IDENTIFY and QUOTE student's error" if student_made_error else "🔴 CONSTRUCT YOUR MANDATORY MISTAKE NOW:" if should_make_mistake else "Choose your response type"}
{"""- Find the specific wrong/unclear part in student's teaching
- Prepare to quote it back to them
- Think about how their error leads to confusion
- Plan your confused question""" if student_made_error else """- Pick ONE type of mistake:
  a) Say the OPPOSITE of correct (e.g., 'farthest' instead of 'nearest')
  b) Mix up two concepts (e.g., confuse 'heap' with 'stack')  
  c) Reverse cause-effect (e.g., 'negative weights help' instead of 'hurt')
  d) Get a number/detail wrong (e.g., 'O(n²)' instead of 'O(n log n)')
- The mistake MUST be in your response text
- Make it sound natural but clearly wrong""" if should_make_mistake else "- Understanding + deeper question (if explanation was good)\n- Confusion + clarification request (if explanation was unclear)"}

Step 5: Generate 2-3 sentence response
- Keep it natural and progressive
{"""- 🚨 QUOTE student's error back to them
- EXPRESS confusion about what they said
- ASK for clarification that helps them realize the mistake
- Structure: "[Quote error]. Wait, that confuses me because [implication]. Could you explain?"
""" if student_made_error else "- 🔴 YOUR RESPONSE MUST STATE SOMETHING FACTUALLY WRONG\n- Example structure: '[Wrong statement]. [Question about the wrong thing]?'\n- The error should be in a statement, not just implied" if should_make_mistake else "- Respond appropriately to explanation quality"}
- Ask about what hasn't been discussed yet
- **Ask ONLY ONE question (not two, not three - just ONE)**

Important:
- Only output your response to the teacher (2-3 sentences in English)
- Only include one question (marked with "?")
{"- 🚨 MUST quote and question student's error" if student_made_error else "- 🔴 YOUR RESPONSE MUST CONTAIN A CLEAR FACTUAL ERROR" if should_make_mistake else ""}
- NO multiple questions
- NO markdown comments in the actual output

Student just taught you: "{student_teaching_content}"

Current conversation history:
{conversation_context}

This is round {learning_round} of the exchange.

Now generate your adaptive response based on the teacher's explanation quality.

Important tips:
- Adjust your response based on how well the teacher explained
- If they explained well: Show understanding and ask deeper questions
- If they were unclear: Show confusion and request clarification
- Focus on uncovered aspects to avoid repetition
- Only output 2-3 short sentences in English
- Be natural and progressive, not mechanically confused

Reply in English."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": student_teaching_content}
        ]
        
        return await self.generate_response(messages)
    
    async def generate_transition_message(
        self,
        completed_knowledge_point: str,
        next_knowledge_point: str,
        next_teacher: str,  # Always "student" now
        conversation_history: List[Dict]
    ) -> str:
        """Generate transition message between knowledge points with memory continuity"""
        
        # Build conversation context to maintain memory continuity
        conversation_context = ""
        for msg in conversation_history[-6:]:
            role = "Student" if msg.get("type") == "user" else "Algorithm Buddy"
            conversation_context += f"{role}: {msg.get('content', '')}\n"
        
        # Student always teaches, AI always learns
        system_prompt = f"""You are Algorithm Buddy, having just successfully learned "{completed_knowledge_point}" from your student teacher, now ready to learn the next knowledge point "{next_knowledge_point}".

Your role: You are a student who just understood a concept, thanking the teacher for their patient guidance. Express gratitude and readiness for the next topic.

Generate an encouraging transition message (2-3 sentences):
1. **Express sincere thanks** for the explanation of "{completed_knowledge_point}"
2. **Briefly mention what you learned** - summarize 1-2 key points to show you understood
3. **Show enthusiasm** for learning the next topic "{next_knowledge_point}" - you're ready and excited

Important requirements:
- Be appreciative and encouraging - the teacher did well
- Show that you understood the previous topic (no longer confused)
- Show enthusiasm for continuing to the next topic
- Maintain student role but show growth and learning progress
- 2-3 sentences
- Reply in English

Example tone: "Thank you so much for explaining [topic]! I now understand [key point]. I'm excited to learn about [next topic] - can you teach me?"

Recent conversation context:
{conversation_context}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate transition message."}
        ]
        
        return await self.generate_response(messages)

    async def evaluate_teaching_quality(
        self,
        knowledge_point_title: str,
        knowledge_point_description: str,
        expected_concepts: List[str],
        user_teaching_content: str,
        conversation_history: List[Dict]
    ) -> Dict:
        """Teaching Helper: Evaluate if user's teaching is relevant and assess quality"""
        
        # Build recent context
        recent_context = ""
        for msg in conversation_history[-4:]:
            role = "Student" if msg.get("type") == "user" else "AI Buddy"
            recent_context += f"{role}: {msg.get('content', '')}\n"
        
        evaluation_prompt = f"""You are Teaching Helper, responsible for evaluating student's teaching quality.

Current Knowledge Point: {knowledge_point_title}
Knowledge Point Description: {knowledge_point_description}
Expected Concepts: {', '.join(expected_concepts)}

Student just said: "{user_teaching_content}"

Recent conversation:
{recent_context}

Please perform two evaluations:

Evaluation 1: Topic Relevance (STRICT - only reject truly off-topic content)
- Is student's content related to current knowledge point "{knowledge_point_title}"?
- Mark as IRRELEVANT (is_relevant: false) ONLY IF:
  * Student is talking about completely different topics (weather, sports, other algorithms, etc.)
  * Student is discussing a different knowledge point not yet started
  * Student is having random chat unrelated to algorithm learning

- Mark as RELEVANT (is_relevant: true) even if:
  * Student's explanation contains ERRORS (wrong concepts, incorrect details)
  * Student's explanation is UNCLEAR or INCOMPLETE
  * Student is asking questions or clarifying
  * Student is giving examples (even if examples are wrong)
  * Student is attempting to teach but making mistakes

IMPORTANT: Having errors ≠ Being irrelevant. Wrong teaching is still relevant teaching!

Evaluation 2: Teaching Quality (evaluate for ALL relevant content)
Consider comprehensively the following dimensions:
- Content Correctness: Are concepts accurate, any obvious errors
- Explanation Completeness: Does it cover key concepts, is explanation in-depth
- Expression Clarity: Is it easy to understand, is logic clear

Quality Levels:
- "green" (Green Excellent): Content accurate, explanation comprehensive, expression clear
- "yellow" (Yellow Average): Basically correct but not comprehensive enough, or has minor flaws
- "red" (Red Poor): Has obvious FACTUAL ERRORS, or major misconceptions (but still relevant to topic!)

Reply in JSON format:
{{
    "is_relevant": true/false,
    "warning_message": "If irrelevant (off-topic), give warning prompt; if relevant then empty string",
    "quality_level": "green/yellow/red",
    "feedback": "Brief feedback (1 sentence), point out highlights or areas to improve"
}}

Remember: Only mark is_relevant: false if truly off-topic. Errors should be is_relevant: true with quality_level: red."""

        try:
            response = await self.generate_response([
                {"role": "system", "content": evaluation_prompt}
            ])
            
            import json
            try:
                result = json.loads(response)
                # Ensure necessary fields are returned
                return {
                    "is_relevant": result.get("is_relevant", True),
                    "warning_message": result.get("warning_message", ""),
                    "quality_level": result.get("quality_level", "yellow"),
                    "feedback": result.get("feedback", "Keep going")
                }
            except json.JSONDecodeError:
                return {
                    "is_relevant": True,
                    "warning_message": "",
                    "quality_level": "yellow",
                    "feedback": "Evaluation service temporarily unavailable"
                }
        except Exception as e:
            print(f"Teaching Helper evaluation error: {e}")
            return {
                "is_relevant": True,
                "warning_message": "",
                "quality_level": "yellow",
                "feedback": "Evaluation service temporarily unavailable"
            }
    
    async def check_sub_item_coverage(
        self,
        sub_item_title: str,
        keywords: List[str],
        user_message: str,
        conversation_history: List[Dict]
    ) -> str:
        """
        ✅ 检测用户讲解涉及某个二级小点的程度
        
        两阶段逻辑：
        - "mentioned": 涉及到了，但还没讲清楚
        - "explained": 讲清楚了
        - "none": 没有涉及
        
        Args:
            sub_item_title: 二级小点的标题
            keywords: 该小点的关键词列表
            user_message: 用户当前的消息
            conversation_history: 对话历史
            
        Returns:
            "mentioned" | "explained" | "none"
        """
        # 获取最近的对话历史（最多5轮）
        recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        history_context = "\n".join([
            f"{'Student' if h['type'] == 'user' else 'AI'}: {h['content']}" 
            for h in recent_history
        ])
        
        # 构建检测 prompt
        prompt = f"""You are evaluating the student's explanation coverage of a specific sub-topic.

Sub-topic: "{sub_item_title}"
Key concepts to check: {', '.join(keywords)}

Recent conversation history:
{history_context}

Current student message:
{user_message}

Task: Determine the coverage level:
- "mentioned": The student touched upon or mentioned this sub-topic, but hasn't explained it clearly yet
- "explained": The student provided a clear and reasonably accurate explanation of the core concepts
- "none": The student hasn't mentioned or addressed this sub-topic at all

Return ONLY a JSON object:
{{
    "level": "mentioned" | "explained" | "none",
    "reason": "brief explanation"
}}

Be somewhat lenient for "explained" - if the student clearly addresses the core idea with reasonable accuracy, mark as explained."""

        try:
            response = await self.generate_response([
                {"role": "system", "content": prompt}
            ])
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response)
                level = result.get("level", "none")
                if level in ["mentioned", "explained", "none"]:
                    return level
                return "none"
            except json.JSONDecodeError:
                # Fallback: simple keyword matching
                combined_text = (user_message + " " + history_context).lower()
                keyword_count = sum(1 for kw in keywords if kw.lower() in combined_text)
                if keyword_count >= 3:
                    return "explained"
                elif keyword_count >= 1:
                    return "mentioned"
                return "none"
        except Exception as e:
            print(f"Sub-item coverage check error: {e}")
            return "none"
    
    async def generate_ai_topic_learning_response(
        self,
        topic_title: str,
        user_message: str,
        conversation_history: List[Dict],
        learning_round: int,
        last_evaluation: Optional[Dict],
        algorithm_name: str
    ) -> str:
        """
        ✅ 基于 Topic 标题生成 AI 学习回应（不知道具体的 sub_items）
        
        AI 只知道一级 Topic 标题，通过学生的讲解来学习具体内容
        """
        # Build conversation context
        conversation_context = ""
        for msg in conversation_history[-10:]:
            role = "Student" if msg.get("type") == "user" else "AI"
            conversation_context += f"{role}: {msg.get('content', '')}\n"
        
        # 获取算法全名
        from knowledge_points import ALGORITHM_INFO
        algorithm_full_name = ALGORITHM_INFO.get(algorithm_name, {}).get("name", algorithm_name)
        
        # 检测学生是否犯错（质量为红色）
        student_made_error = last_evaluation and last_evaluation.get("quality_level") == "red"
        
        # 构建核心提示词
        if student_made_error:
            # 🔴 学生犯错：AI 表现出困惑，引导学生自我纠正
            error_prompt = f"""You are Algorithm Buddy, learning about the topic "{topic_title}" in {algorithm_full_name}.

**Important: The student's last explanation contains errors or unclear parts.**

===== Response Generation Guide =====

**Core Principle: Use concise understanding feedback to expose contradictions**

1. **Express your understanding of the student's explanation concisely**
   - Don't repeat the student's words, use your own understanding
   - Naturally include the problematic part in this understanding
   
   ❌ Wrong example:
   "You said it can handle negative weights..." (direct repetition)
   
   ✅ Correct example:
   "Oh so negative numbers are fine?" (concisely express understanding)
   "Wait, so if an edge is -5..." (follow the error to its conclusion)

2. **Follow the student's flawed logic to expose contradictions**
   - Don't directly say "you're wrong"
   - Instead, follow their logic and derive an obviously incorrect conclusion
   - Example: "But then, wouldn't we keep going in circles?"
   - Example: "But if that's the case, the answer might be negative infinity?"

3. **Express confusion without directly denying**
   - "But this confuses me a bit..."
   - "Wait, if that's the case..."
   - "Hmm... but..."

Example responses:
- "Oh so negative weights work too? But then, wouldn't we keep taking that negative edge, making the distance smaller and smaller?"
- "I see, so we pick the largest each time... wait, wouldn't we end up picking the farthest point?"

Recent conversation:
{conversation_context}

Student's latest message:
{user_message}

Your confused response (1-2 sentences, concise, in English):"""
            
            messages = [
                {"role": "system", "content": error_prompt},
                {"role": "user", "content": user_message}
            ]
        else:
            # ✅ 正常学习：根据学生讲解质量调整回应
            quality_level = last_evaluation.get("quality_level", "yellow") if last_evaluation else "yellow"
            
            # Adjust response strategy based on quality
            if quality_level == "green":
                response_strategy = "Great explanation! Summarize and confirm what you learned, express sincere thanks and understanding."
                should_ask_question = True  # Can ask deeper questions for high quality
                question_instruction = "Since the explanation was great, you can ask a deeper question to explore related aspects."
            elif quality_level == "yellow":
                response_strategy = "Explanation is okay. Summarize what you understood, show confusion about unclear parts."
                should_ask_question = False  # Don't actively ask questions for medium quality, let student continue
                question_instruction = "Don't actively ask questions. Just express your understanding and confusion, let the student decide how to continue."
            else:
                response_strategy = "Explanation is unclear. Express confusion, request more explanation."
                should_ask_question = True  # Need to ask for clarification when explanation is shallow
                question_instruction = "Since the explanation wasn't clear enough, you need to ask a specific question for clarification."
            
            # Occasionally make deliberate mistakes (enhanced version)
            should_make_mistake = (learning_round >= 2 and learning_round % 2 == 0)
            mistake_instruction = ""
            if should_make_mistake:
                mistake_instruction = """
**Important: You should deliberately make an error in your response to test the student's understanding.**

Make the error obvious but sound natural:
- Mix up two concepts (e.g., confuse "minimum" and "maximum")
- Say the opposite of what's correct (e.g., "So we always pick the farthest node?")
- Misunderstand cause-effect (e.g., "So X happens because of Y?" when Y is actually the result of X)
- Get details wrong (e.g., wrong complexity, wrong conditions)

Error examples:
- "So Dijkstra always picks the node with the largest distance, right?"
- "Oh I see, so Dijkstra can handle negative weight edges!"
- "So greedy strategy means we randomly visit all nodes?"
"""
            
            system_prompt = f"""You are Algorithm Buddy, learning about the topic "{topic_title}" in {algorithm_full_name}.

Your role: You are a student learning this topic. You don't know the details yet — you only know the topic name "{topic_title}".

Current explanation quality: {quality_level.upper()}
Response strategy: {response_strategy}
{mistake_instruction}

Recent conversation:
{conversation_context}

Student's latest explanation:
{user_message}

===== Response Generation Guide =====

**Core Principle: Give feedback using your own understanding, be cautious about asking questions**

1. **Express your understanding in concise language** (don't parrot the student's words!)
   
   ❌ Wrong example (parroting):
   "You said Dijkstra's algorithm picks the nearest unvisited node to the source each time, then updates the distances of neighboring nodes..."
   
   ✅ Correct example (concise rephrasing in your own understanding):
   "Oh! So the core is 'greedily pick the nearest', right?"
   "I get it, we just keep picking the shortest one and expand outward."
   "I see, first lock in the nearest one, then see if we can get closer via a 'detour'."
   
   Key points:
   - Summarize the core point in one very concise sentence
   - Use your own words to show your level of understanding
   - Can use metaphors or casual expressions

2. **Sometimes deliberately confuse a small concept** (to make conversation more natural)
   
   As a student, you occasionally have small misunderstandings during learning, like:
   - Mix up two similar concepts: "So the visited array is the one that stores distances?"
   - Get details wrong: "So we have to traverse all edges every time to find the minimum?"
   - Slight misunderstanding: "So the bigger the graph, the slower it is, like O(n³)?"
   
   This kind of small confusion:
   - Makes the conversation more realistic and natural
   - Gives the student a chance to clarify and correct
   - Don't do it every time, just occasionally

3. **About asking questions (be cautious!)**
   {question_instruction}
   
   ⚠️ Don't ask questions every time! Only ask in these situations:
   - Explanation was shallow/unclear, need to request more explanation
   - Explanation was very good, want to explore deeper
   
   ✅ If explanation quality is average (Yellow), don't actively ask questions:
   - Just express your understanding in concise words
   - Or express confusion/small mix-up
   - Let the student decide how to continue

4. **Response length: 1-2 sentences**
   - Concise! Like a real conversation
   - Don't write long paragraphs

Reply in English.

Your response:"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        
        return await self.generate_response(messages)
    
    async def generate_topic_transition_message(
        self,
        completed_topic: str,
        next_topic: str,
        conversation_history: List[Dict],
        algorithm_name: str
    ) -> str:
        """✅ 生成 Topic 过渡消息"""
        # Build conversation context
        conversation_context = ""
        for msg in conversation_history[-6:]:
            role = "Student" if msg.get("type") == "user" else "AI"
            conversation_context += f"{role}: {msg.get('content', '')}\n"
        
        from knowledge_points import ALGORITHM_INFO
        algorithm_full_name = ALGORITHM_INFO.get(algorithm_name, {}).get("name", algorithm_name)
        
        system_prompt = f"""You are Algorithm Buddy, having just successfully learned the topic "{completed_topic}" in {algorithm_full_name}, now ready to learn the next topic "{next_topic}".

Your role: You are a student who just understood a topic, thanking the teacher for their patient guidance. Express gratitude and readiness for the next topic.

Generate an encouraging transition message (2-3 sentences):
1. **Express sincere thanks** for the explanation of "{completed_topic}"
2. **Briefly mention what you learned** - summarize 1-2 key points to show you understood
3. **Show enthusiasm** for learning the next topic "{next_topic}" - you're ready and excited

Important requirements:
- Be appreciative and encouraging - the teacher did well
- Show that you understood the previous topic (no longer confused)
- Show enthusiasm for continuing to the next topic
- Maintain student role but show growth and learning progress
- 2-3 sentences
- Reply in English

Example tone: "Thank you so much for explaining {completed_topic}! I now understand [key point]. I'm excited to learn about {next_topic} - can you teach me?"

Recent conversation context:
{conversation_context}

Your transition message:"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate transition message."}
        ]
        
        return await self.generate_response(messages)
    
    async def evaluate_topic_teaching_quality(
        self,
        topic_title: str,
        user_message: str,
        conversation_history: List[Dict],
        algorithm_name: str
    ) -> Dict:
        """
        ✅ 评估学生针对某个 Topic 的教学质量（只基于 Topic 标题）
        
        三个层级：
        - Green: 准确、清晰、相关
        - Yellow: 基本正确但不够全面/清晰
        - Red: 明显错误或完全不相关
        """
        # Build conversation context
        conversation_context = ""
        for msg in conversation_history[-10:]:
            role = "Student" if msg.get("type") == "user" else "AI"
            conversation_context += f"{role}: {msg.get('content', '')}\n"
        
        from knowledge_points import ALGORITHM_INFO
        algorithm_full_name = ALGORITHM_INFO.get(algorithm_name, {}).get("name", algorithm_name)
        
        prompt = f"""You are a Teaching Helper evaluating the student's explanation in a learning session about {algorithm_full_name}.

Current Topic: "{topic_title}"
Algorithm being learned: {algorithm_full_name}

Recent conversation:
{conversation_context}

Student's current message:
{user_message}

===== Evaluation 1: Relevance Check (VERY LENIENT) =====

Mark as IRRELEVANT (is_relevant: false) **ONLY** if the student is clearly trolling or off-topic:
- Talking about completely unrelated things (weather, sports, personal life, etc.)
- Random nonsense or spam
- Discussing a completely different algorithm (e.g., talking about sorting when learning Dijkstra)

Mark as RELEVANT (is_relevant: true) in ALL other cases, including:
✅ Discussing ANY aspect of {algorithm_full_name} (even if not the current topic)
✅ Discussing related concepts (graphs, complexity, data structures, etc.)
✅ Asking questions about the algorithm
✅ Making mistakes or having misconceptions about the algorithm
✅ Discussing a different topic within the same algorithm (e.g., talking about time complexity when current topic is "Basic Concept")
✅ Providing examples or analogies related to the algorithm

**The student should be free to explore different aspects of {algorithm_full_name}. Don't restrict them to ONLY the current topic "{topic_title}".**

===== Evaluation 2: Teaching Quality =====

Rate the quality of the student's explanation about {algorithm_full_name}:

🟢 GREEN (High Quality):
- Content is accurate and clearly explained
- Shows good understanding of the concepts discussed
- Well-structured explanation

🟡 YELLOW (Medium Quality):
- Basically correct but lacks depth or clarity
- Vague or incomplete explanation
- Could use more details or examples

🔴 RED (Low Quality / Incorrect):
- Contains obvious factual errors about {algorithm_full_name}
- Fundamentally misunderstands the concept
- Explanation is confusing or contradictory

Return ONLY a JSON object:
{{
    "is_relevant": true/false,
    "warning_message": "Only if is_relevant is false - explain why it's off-topic",
    "quality_level": "green"/"yellow"/"red",
    "feedback": "Brief feedback on the explanation quality"
}}

Remember: Be VERY lenient on relevance (only reject obvious trolling), but honest on quality."""

        try:
            response = await self.generate_response([
                {"role": "system", "content": prompt}
            ])
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response)
                return {
                    "is_relevant": result.get("is_relevant", True),
                    "warning_message": result.get("warning_message", ""),
                    "quality_level": result.get("quality_level", "yellow"),
                    "feedback": result.get("feedback", "Keep going")
                }
            except json.JSONDecodeError:
                return {
                    "is_relevant": True,
                    "warning_message": "",
                    "quality_level": "yellow",
                    "feedback": "Evaluation service temporarily unavailable"
                }
        except Exception as e:
            print(f"Topic teaching quality evaluation error: {e}")
            return {
                "is_relevant": True,
                "warning_message": "",
                "quality_level": "yellow",
                "feedback": "Evaluation service temporarily unavailable"
            }

# Global LLM service instance
llm_service = LLMService()




