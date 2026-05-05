class Accessory:
    def __init__(self, name, accessory_family=None, rarity=None, requirements=None, stats=None):
        self.name = name
        self.accessory_family = accessory_family
        self.rarity = rarity
        self.requirements = requirements if requirements is not None else {}
        self.stats = stats if stats is not None else {}
    
    def set_accessory_family(self, accessory_family):
        self.accessory_family = accessory_family
    
    def set_rarity(self, rarity):
        self.rarity = rarity
    
    def add_requirement(self, requirement_type, value):
        self.requirements[requirement_type] = value
    
    def add_stat(self, stat_type, value):
        self.stats[stat_type] = value
    
    def get_requirements(self):
        return self.requirements
    
    def get_stats(self):
        return self.stats
    
    def get_rarity(self):
        return self.rarity
    
    def get_accessory_family(self):
        return self.accessory_family
    
    def __str__(self):
        return f"Accessory(name={self.name}, family={self.accessory_family}, rarity={self.rarity})"
    
    def __repr__(self):
        return f"Accessory(name='{self.name}', accessory_family={self.accessory_family}, rarity={self.rarity}, requirements={self.requirements}, stats={self.stats})"