from src.config import *

class ResearchSystem:
    def __init__(self):
        # Topic: (Cost, Duration, Description)
        self.topics = {
            "Basic Alchemy": (50, 5, "Unlocks basic potion recipes."),
            "Advanced Alchemy": (100, 10, "Unlocks advanced potion recipes."),
            "Herbology": (75, 8, "Unlocks planting of Red and Blue Herbs."),
            "Rare Herbs": (150, 15, "Unlocks planting of Rare Herbs.")
        }
        self.completed_research = []
        self.current_research = None
        self.research_timer = 0
        self.research_duration = 0
        
    def can_research(self, topic, intelligence):
        # Placeholder: Check intelligence requirement (e.g. 10 per tier)
        return topic not in self.completed_research
        
    def start_research(self, topic):
        if topic in self.topics:
            cost, duration, _ = self.topics[topic]
            self.current_research = topic
            self.research_duration = duration * 60 # Frames
            self.research_timer = 0
            
    def update(self, intelligence, fairies_caught=0, spawn_fairies=False):
        if self.current_research:
            # Base speed + Fairy Boost
            speed = 1 + (fairies_caught * FAIRY_RESEARCH_BOOST)
            self.research_timer += speed
            
            if self.research_timer >= self.research_duration:
                self.completed_research.append(self.current_research)
                print(f"Research Complete: {self.current_research}")
                self.current_research = None
                self.research_timer = 0
                
    def get_progress(self):
        if self.current_research and self.research_duration > 0:
            return min(1.0, self.research_timer / self.research_duration)
        return 0
