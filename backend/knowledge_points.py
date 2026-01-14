# Algorithm Knowledge Points Definition
from typing import List, Dict, Optional
from enum import Enum

class KnowledgePointStatus(Enum):
    NOT_STARTED = "not_started"
    AI_TEACHING = "ai_teaching" 
    STUDENT_TEACHING = "student_teaching"
    COMPLETED = "completed"

# Three states for sub-items
class SubItemStatus(Enum):
    LOCKED = "locked"  # Not viewed & not mentioned (blurred by default)
    MANUALLY_VIEWED = "manuallyViewed"  # Manually clicked to view by student
    REVEALED_BY_LLM = "revealedByLLM"  # Unlocked through explanation (exploration unlock)

class KnowledgePoint:
    def __init__(self, id: str, title: str, description: str, ai_teaching_content: str, expected_student_concepts: List[str]):
        self.id = id
        self.title = title
        self.description = description
        self.ai_teaching_content = ai_teaching_content
        self.expected_student_concepts = expected_student_concepts
        self.status = KnowledgePointStatus.NOT_STARTED
        self.ai_taught = False
        self.student_taught = False

# Dijkstra Algorithm Knowledge Points - Progressive from shallow to deep, no overlap
DIJKSTRA_KNOWLEDGE_POINTS = [
    KnowledgePoint(
        id="graph_basics",
        title="Graph Basics and Problem Definition",
        description="Understanding graphs, weighted edges, and the shortest path problem",
        ai_teaching_content="",
        expected_student_concepts=["graph", "vertex", "edge", "weight", "shortest path", "source vertex", "destination"]
    ),
    
    KnowledgePoint(
        id="greedy_strategy", 
        title="Greedy Strategy",
        description="Understanding the greedy approach: always choosing the nearest unvisited vertex",
        ai_teaching_content="",
        expected_student_concepts=["greedy choice", "locally optimal", "non-negative weights", "why greedy works"]
    ),
    
    KnowledgePoint(
        id="algorithm_steps",
        title="Algorithm Steps and Execution",
        description="The step-by-step process: initialization, selection, and distance updates",
        ai_teaching_content="",
        expected_student_concepts=["initialization", "distance array", "visited set", "relaxation", "iterative process"]
    ),
    
    KnowledgePoint(
        id="priority_queue",
        title="Priority Queue Data Structure",
        description="How priority queue (min-heap) efficiently finds the minimum distance vertex",
        ai_teaching_content="",
        expected_student_concepts=["priority queue", "min heap", "extract minimum", "decrease key", "efficiency improvement"]
    ),
    
    KnowledgePoint(
        id="complexity_analysis",
        title="Time and Space Complexity",
        description="Analyzing the algorithm's efficiency with different implementations",
        ai_teaching_content="",
        expected_student_concepts=["time complexity", "O((V+E)log V)", "space complexity", "vertices V", "edges E"]
    )
]

# Quick Sort Knowledge Points - Progressive learning path
QUICKSORT_KNOWLEDGE_POINTS = [
    KnowledgePoint(
        id="divide_conquer_concept",
        title="Divide and Conquer Concept",
        description="Understanding the divide-and-conquer paradigm in sorting",
        ai_teaching_content="",
        expected_student_concepts=["divide and conquer", "problem decomposition", "recursive approach", "sorting strategy"]
    ),
    
    KnowledgePoint(
        id="pivot_selection",
        title="Pivot Selection Strategy",
        description="Choosing a pivot element and its impact on performance",
        ai_teaching_content="",
        expected_student_concepts=["pivot element", "selection methods", "first/last/median", "random pivot", "performance impact"]
    ),
    
    KnowledgePoint(
        id="partitioning_process",
        title="Partitioning Process",
        description="How to partition array around pivot: elements smaller on left, larger on right",
        ai_teaching_content="",
        expected_student_concepts=["partitioning", "two pointers", "swap operations", "in-place sorting", "pivot position"]
    ),
    
    KnowledgePoint(
        id="recursion_base_case",
        title="Recursion and Base Case",
        description="Recursive calls on sub-arrays and when to stop recursion",
        ai_teaching_content="",
        expected_student_concepts=["recursive calls", "base case", "sub-arrays", "call stack", "termination condition"]
    ),
    
    KnowledgePoint(
        id="performance_analysis",
        title="Performance Analysis",
        description="Best, average, and worst-case time complexity analysis",
        ai_teaching_content="",
        expected_student_concepts=["best case O(n log n)", "average case", "worst case O(n²)", "space complexity", "optimization"]
    )
]

# Merge Sort Knowledge Points - Progressive learning path
MERGESORT_KNOWLEDGE_POINTS = [
    KnowledgePoint(
        id="divide_strategy",
        title="Divide Strategy",
        description="Splitting array into halves recursively until single elements",
        ai_teaching_content="",
        expected_student_concepts=["divide phase", "split into halves", "recursive division", "single element arrays", "divide until trivial"]
    ),
    
    KnowledgePoint(
        id="merge_operation",
        title="Merge Operation",
        description="Combining two sorted sub-arrays into one sorted array",
        ai_teaching_content="",
        expected_student_concepts=["merge process", "two sorted arrays", "comparison", "temporary array", "combining results"]
    ),
    
    KnowledgePoint(
        id="recursive_structure",
        title="Recursive Structure",
        description="How recursion builds the complete sorting through divide and merge phases",
        ai_teaching_content="",
        expected_student_concepts=["recursion tree", "divide phase", "conquer phase", "merge phase", "call hierarchy"]
    ),
    
    KnowledgePoint(
        id="stability_property",
        title="Stability in Sorting",
        description="Understanding why merge sort is stable and why it matters",
        ai_teaching_content="",
        expected_student_concepts=["stable sort", "equal elements", "relative order", "stability importance", "comparison with unstable sorts"]
    ),
    
    KnowledgePoint(
        id="complexity_tradeoffs",
        title="Time and Space Complexity",
        description="Guaranteed O(n log n) time but requires O(n) extra space",
        ai_teaching_content="",
        expected_student_concepts=["time complexity O(n log n)", "space complexity O(n)", "auxiliary space", "guaranteed performance", "trade-offs"]
    )
]

class KnowledgePointManager:
    def __init__(self):
        self.knowledge_points = DIJKSTRA_KNOWLEDGE_POINTS.copy()
        self.current_index = 0
        self.completed_count = 0
    
    def get_teacher_for_knowledge_point(self, index: int) -> str:
        """Determine who should teach this knowledge point (student always teaches)"""
        # Student teaches all knowledge points
        return "student"
    
    def get_current_teacher(self) -> str:
        """Get who should teach the current knowledge point"""
        return self.get_teacher_for_knowledge_point(self.current_index)
    
    def get_current_knowledge_point(self) -> Optional[KnowledgePoint]:
        if self.current_index < len(self.knowledge_points):
            return self.knowledge_points[self.current_index]
        return None
    
    def get_all_knowledge_points(self) -> List[KnowledgePoint]:
        return self.knowledge_points
    
    def mark_ai_teaching_complete(self):
        current = self.get_current_knowledge_point()
        if current:
            current.ai_taught = True
            current.status = KnowledgePointStatus.STUDENT_TEACHING
    
    def mark_student_teaching_complete(self):
        current = self.get_current_knowledge_point()
        if current:
            current.student_taught = True
            current.status = KnowledgePointStatus.COMPLETED
            self.completed_count += 1
            self.current_index += 1
    
    def is_all_completed(self) -> bool:
        return self.completed_count >= len(self.knowledge_points)
    
    def get_progress_stats(self) -> Dict:
        return {
            "total_points": len(self.knowledge_points),
            "completed_points": self.completed_count,
            "current_point": self.current_index + 1 if self.current_index < len(self.knowledge_points) else len(self.knowledge_points),
            "progress_percentage": (self.completed_count / len(self.knowledge_points)) * 100,
            "knowledge_points_status": [
                {
                    "id": kp.id,
                    "title": kp.title,
                    "status": kp.status.value,
                    "ai_taught": kp.ai_taught,
                    "student_taught": kp.student_taught
                }
                for kp in self.knowledge_points
            ]
        }

# Algorithm information definition
ALGORITHM_INFO = {
    "dijkstra": {
        "name": "Dijkstra's Algorithm",
        "description": "Shortest path algorithm in graph theory",
        "icon": "🗺️"
    },
    "quicksort": {
        "name": "Quick Sort",
        "description": "Efficient divide-and-conquer sorting algorithm",
        "icon": "⚡"
    },
    "mergesort": {
        "name": "Merge Sort", 
        "description": "Stable divide-and-conquer sorting algorithm",
        "icon": "🔀"
    }
}

# Algorithm knowledge points mapping
ALGORITHM_KNOWLEDGE_POINTS = {
    "dijkstra": DIJKSTRA_KNOWLEDGE_POINTS,
    "quicksort": QUICKSORT_KNOWLEDGE_POINTS,
    "mergesort": MERGESORT_KNOWLEDGE_POINTS
}

# ========== Two-level Structure Definition: Progressive Topic Board ==========

class SubItem:
    """Sub-item: The smallest unit that can be independently evaluated and unlocked"""
    def __init__(self, id: str, title: str, keywords: List[str]):
        self.id = id
        self.title = title  # Specific teaching point name
        self.keywords = keywords  # Keywords used by LLM for detection
        self.status = SubItemStatus.LOCKED
        self.completed = False  # LLM determines "explained clearly"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "completed": self.completed
        }

class Topic:
    """Topic: Structural skeleton, visible to students"""
    def __init__(self, id: str, title: str, sub_items: List[SubItem]):
        self.id = id
        self.title = title  # e.g.: "Basic Concept"
        self.sub_items = sub_items
        self.unlocked = False  # Whether this Topic is allowed to be taught
    
    def is_all_completed(self) -> bool:
        """Check if all sub-items under this Topic are completed"""
        return all(item.completed for item in self.sub_items)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "unlocked": self.unlocked,
            "sub_items": [item.to_dict() for item in self.sub_items],
            "all_completed": self.is_all_completed()
        }

# ========== Dijkstra Two-level Structure ==========
DIJKSTRA_TOPICS = [
    Topic(
        id="basic_concept",
        title="Basic Concept",
        sub_items=[
            SubItem("dijkstra_definition", "What is Dijkstra's Algorithm", 
                   ["dijkstra", "shortest path", "algorithm definition", "purpose"]),
            SubItem("graph_structure", "Graph Structure", 
                   ["graph", "vertex", "edge", "weighted graph", "directed"])
        ]
    ),
    Topic(
        id="algorithm_process",
        title="Algorithm Process",
        sub_items=[
            SubItem("greedy_choice", "Greedy Strategy", 
                   ["greedy", "locally optimal", "nearest vertex", "greedy choice"]),
            SubItem("relaxation", "Relaxation Operation", 
                   ["relaxation", "update distance", "distance array", "edge relaxation"]),
            SubItem("execution_steps", "Step-by-Step Execution", 
                   ["initialization", "visited set", "iterative process", "algorithm steps"])
        ]
    ),
    Topic(
        id="time_complexity",
        title="Time Complexity",
        sub_items=[
            SubItem("basic_complexity", "Basic Time Analysis", 
                   ["time complexity", "O((V+E)log V)", "vertices", "edges"]),
            SubItem("priority_queue_impact", "Priority Queue Impact", 
                   ["priority queue", "min heap", "efficiency", "optimization"])
        ]
    ),
    Topic(
        id="space_complexity",
        title="Space Complexity",
        sub_items=[
            SubItem("space_analysis", "Space Requirements", 
                   ["space complexity", "distance array", "visited set", "memory usage", "O(V)"])
        ]
    ),
    Topic(
        id="use_cases",
        title="Use Cases",
        sub_items=[
            SubItem("practical_applications", "Real-World Applications", 
                   ["routing", "GPS", "network", "shortest route", "applications"]),
            SubItem("limitations", "Algorithm Limitations", 
                   ["non-negative weights", "limitations", "when not to use", "negative edges"])
        ]
    )
]

# ========== Quick Sort Two-level Structure ==========
QUICKSORT_TOPICS = [
    Topic(
        id="basic_concept",
        title="Basic Concept",
        sub_items=[
            SubItem("quicksort_definition", "What is Quick Sort", 
                   ["quick sort", "sorting algorithm", "divide and conquer"]),
            SubItem("comparison_sorting", "Comparison-based Sorting", 
                   ["comparison", "in-place", "sorting strategy"])
        ]
    ),
    Topic(
        id="algorithm_process",
        title="Algorithm Process",
        sub_items=[
            SubItem("pivot_selection", "Pivot Selection", 
                   ["pivot", "pivot element", "selection strategy", "random pivot"]),
            SubItem("partitioning", "Partitioning Process", 
                   ["partition", "two pointers", "swap", "partitioning"]),
            SubItem("recursion", "Recursive Calls", 
                   ["recursion", "recursive", "sub-arrays", "base case"])
        ]
    ),
    Topic(
        id="time_complexity",
        title="Time Complexity",
        sub_items=[
            SubItem("average_case", "Average Case Analysis", 
                   ["average case", "O(n log n)", "expected performance"]),
            SubItem("worst_case", "Worst Case Analysis", 
                   ["worst case", "O(n²)", "sorted array", "poor pivot"])
        ]
    ),
    Topic(
        id="space_complexity",
        title="Space Complexity",
        sub_items=[
            SubItem("space_analysis", "Space Requirements", 
                   ["space complexity", "call stack", "in-place", "O(log n)"])
        ]
    ),
    Topic(
        id="use_cases",
        title="Use Cases",
        sub_items=[
            SubItem("when_to_use", "When to Use Quick Sort", 
                   ["advantages", "fast average", "cache efficiency", "practical choice"]),
            SubItem("optimization", "Optimization Techniques", 
                   ["optimization", "three-way partition", "median-of-three", "hybrid"])
        ]
    )
]

# ========== Merge Sort Two-level Structure ==========
MERGESORT_TOPICS = [
    Topic(
        id="basic_concept",
        title="Basic Concept",
        sub_items=[
            SubItem("mergesort_definition", "What is Merge Sort", 
                   ["merge sort", "stable sort", "divide and conquer"]),
            SubItem("divide_conquer", "Divide and Conquer Paradigm", 
                   ["divide", "conquer", "merge", "paradigm"])
        ]
    ),
    Topic(
        id="algorithm_process",
        title="Algorithm Process",
        sub_items=[
            SubItem("divide_phase", "Divide Phase", 
                   ["split", "divide into halves", "recursive division", "single elements"]),
            SubItem("merge_phase", "Merge Phase", 
                   ["merge", "combine", "sorted arrays", "merge operation"]),
            SubItem("recursion_tree", "Recursion Structure", 
                   ["recursion tree", "call hierarchy", "recursive structure"])
        ]
    ),
    Topic(
        id="time_complexity",
        title="Time Complexity",
        sub_items=[
            SubItem("guaranteed_performance", "Guaranteed O(n log n)", 
                   ["time complexity", "O(n log n)", "guaranteed", "consistent performance"])
        ]
    ),
    Topic(
        id="space_complexity",
        title="Space Complexity",
        sub_items=[
            SubItem("auxiliary_space", "Auxiliary Space Requirement", 
                   ["space complexity", "O(n)", "auxiliary array", "extra space", "memory"])
        ]
    ),
    Topic(
        id="use_cases",
        title="Use Cases",
        sub_items=[
            SubItem("stability", "Stability Property", 
                   ["stable", "stability", "equal elements", "relative order"]),
            SubItem("when_to_use", "When to Use Merge Sort", 
                   ["linked lists", "external sorting", "guaranteed performance", "use cases"])
        ]
    )
]

# ========== Two-level Structure Mapping ==========
ALGORITHM_TOPICS = {
    "dijkstra": DIJKSTRA_TOPICS,
    "quicksort": QUICKSORT_TOPICS,
    "mergesort": MERGESORT_TOPICS
}
