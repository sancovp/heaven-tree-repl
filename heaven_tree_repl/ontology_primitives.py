#!/usr/bin/env python3
"""
Ontology Primitives - Pydantic models for generating ontology triple strings.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class PrimitiveOntologyTriple(BaseModel):
    """Base class for ontological triples with source, relationship_label, target."""
    source: str
    relationship_label: str
    target: str
    
    def __str__(self) -> str:
        """Generate ontology triple string."""
        return f"{self.source} {self.relationship_label} {self.target}"
    
    def to_triple_string(self) -> str:
        """Generate ontology triple string."""
        return str(self)


class IsA(PrimitiveOntologyTriple):
    """IsA relationship: source subclasses target."""
    
    def __init__(self, source: str, target: str, **kwargs):
        super().__init__(
            source=source,
            relationship_label="is_a",
            target=target,
            **kwargs
        )


class PartOf(PrimitiveOntologyTriple):
    """PartOf relationship: source is method/attribute/defined/called in target."""
    alias: Optional[str] = None
    
    def __init__(self, source: str, target: str, alias: Optional[str] = None, **kwargs):
        super().__init__(
            source=source,
            relationship_label="part_of",
            target=target,
            **kwargs
        )
        self.alias = alias
    
    def __str__(self) -> str:
        """Generate ontology triple string with optional alias."""
        if self.alias:
            return f"{self.source} {self.relationship_label} {self.target} as {self.alias}"
        return f"{self.source} {self.relationship_label} {self.target}"


class Instantiates(PrimitiveOntologyTriple):
    """Instantiates relationship: source literally instantiates the thing."""
    
    def __init__(self, source: str, target: str, **kwargs):
        super().__init__(
            source=source,
            relationship_label="instantiates", 
            target=target,
            **kwargs
        )


class Programs(PrimitiveOntologyTriple):
    """Programs relationship: source (OriginationStack) programs target (OntologyEntity)."""
    
    def __init__(self, source: str, target: str, **kwargs):
        super().__init__(
            source=source,
            relationship_label="programs",
            target=target,
            **kwargs
        )


# Higher-level semantic relationships (require LLM reasoning)
class SemanticOntologyTriple(PrimitiveOntologyTriple):
    """Base for semantic relationships that require LLM interpretation."""
    pass


class Embodies(SemanticOntologyTriple):
    """Embodies relationship: semantically observable but not predictable."""
    
    def __init__(self, source: str, target: str, **kwargs):
        super().__init__(
            source=source,
            relationship_label="embodies",
            target=target,
            **kwargs
        )


class Reifies(SemanticOntologyTriple):
    """Reifies relationship: semantically observable but not predictable."""
    
    def __init__(self, source: str, target: str, **kwargs):
        super().__init__(
            source=source,
            relationship_label="reifies",
            target=target,
            **kwargs
        )


class Manifests(SemanticOntologyTriple):
    """Manifests relationship: semantically observable but not predictable."""
    
    def __init__(self, source: str, target: str, **kwargs):
        super().__init__(
            source=source,
            relationship_label="manifests",
            target=target,
            **kwargs
        )


class OriginationStack(BaseModel):
    """
    Collection of triples that bootstrap ontological validation.
    The instantiation pattern that enables existence.
    """
    name: str
    triples: List[PrimitiveOntologyTriple] = []
    is_complete: bool = False
    
    def add_triple(self, triple: PrimitiveOntologyTriple) -> None:
        """Add a triple to the origination stack."""
        self.triples.append(triple)
    
    def validate_completeness(self) -> bool:
        """
        Validate that the origination stack contains the complete bootstrap chain.
        
        Required pattern:
        - is(reality) -is_a-> reality  
        - ...embodies-> partof
        - ...manifests-> instantiates
        - ...reifies-> instantiates
        - ...is_a-> programs
        - ...instantiates-> part_of(reality)
        - ...is_a-> the pattern of is_a
        """
        # For now, check if we have the foundational triples
        has_reality_base = any(
            isinstance(t, IsA) and t.source == "is(reality)" and t.target == "reality" 
            for t in self.triples
        )
        
        has_instantiates_validation = any(
            isinstance(t, Instantiates) and "instantiates" in t.target.lower()
            for t in self.triples
        )
        
        has_programs_relation = any(
            isinstance(t, Programs) 
            for t in self.triples
        )
        
        self.is_complete = has_reality_base and has_instantiates_validation and has_programs_relation
        return self.is_complete
    
    def to_triple_strings(self) -> List[str]:
        """Convert all triples to string representations."""
        return [str(triple) for triple in self.triples]
    
    def __str__(self) -> str:
        """String representation of the entire origination stack."""
        return f"OriginationStack({self.name}): " + " -> ".join(self.to_triple_strings())


class OntologyEntity(BaseModel):
    """
    An entity that exists in the ontological space.
    Must have a complete OriginationStack to be instantiable.
    """
    name: str
    origination_stack: OriginationStack
    entity_type: str = "unknown"
    
    def is_instantiable(self) -> bool:
        """Check if this entity can be instantiated (has complete origination stack)."""
        return self.origination_stack.validate_completeness()
    
    def instantiate(self) -> Optional[str]:
        """
        Instantiate this entity if it has a complete origination stack.
        Returns the instantiation triple string or None if not instantiable.
        """
        if not self.is_instantiable():
            return None
        
        # Create the instantiation relationship
        instantiation_triple = Instantiates(f"${self.name}_instance", self.name)
        return str(instantiation_triple)
    
    def get_programs_relationship(self) -> str:
        """Get the programs relationship for this entity."""
        programs_triple = Programs(self.origination_stack.name, self.name)
        return str(programs_triple)


# Factory functions for easy creation
def is_a(source: str, target: str) -> str:
    """Create IsA ontology triple string."""
    return str(IsA(source, target))


def part_of(source: str, target: str, alias: Optional[str] = None) -> str:
    """Create PartOf ontology triple string."""
    return str(PartOf(source, target, alias))


def instantiates(source: str, target: str) -> str:
    """Create Instantiates ontology triple string.""" 
    return str(Instantiates(source, target))


def programs(source: str, target: str) -> str:
    """Create Programs ontology triple string."""
    return str(Programs(source, target))


def create_foundational_origination_stack() -> OriginationStack:
    """
    Create the foundational origination stack that bootstraps the ontological system.
    
    The bootstrap chain:
    is(reality) -is_a-> reality
    ...embodies-> partof  
    ...manifests-> instantiates
    ...reifies-> instantiates
    ...is_a-> programs
    ...instantiates-> part_of(reality)
    ...is_a-> the pattern of is_a
    """
    stack = OriginationStack(name="foundational_bootstrap")
    
    # The bootstrap sequence
    stack.add_triple(IsA("is(reality)", "reality"))
    stack.add_triple(Embodies("is(reality) -is_a-> reality", "partof"))
    stack.add_triple(Manifests("is(reality) -is_a-> reality -embodies-> partof", "instantiates"))
    stack.add_triple(Reifies("is(reality) -is_a-> reality -embodies-> partof -manifests-> instantiates", "instantiates"))
    stack.add_triple(IsA("is(reality) -is_a-> reality -embodies-> partof -manifests-> instantiates -reifies-> instantiates", "programs"))
    stack.add_triple(Instantiates("is(reality) -is_a-> reality -embodies-> partof -manifests-> instantiates -reifies-> instantiates -is_a-> programs", "part_of(reality)"))
    stack.add_triple(IsA("is(reality) -is_a-> reality -embodies-> partof -manifests-> instantiates -reifies-> instantiates -is_a-> programs -instantiates-> part_of(reality)", "the pattern of is_a"))
    
    return stack


class OntologyRegistry(BaseModel):
    """Registry for dynamically validated relationships and entities."""
    validated_relationships: Dict[str, OntologyEntity] = {}
    validated_entities: Dict[str, OntologyEntity] = {}
    foundational_stack: OriginationStack = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize with foundational bootstrap
        self.foundational_stack = create_foundational_origination_stack()
        
        # Register foundational relationships
        self._register_foundational_relationships()
    
    def _register_foundational_relationships(self):
        """Register the core relationships (is_a, part_of, instantiates, programs)."""
        # STUB: Each foundational relationship gets its own OriginationStack
        for rel_name in ["is_a", "part_of", "instantiates", "programs", "embodies", "reifies", "manifests"]:
            # TODO: Create proper OriginationStack for each relationship
            rel_stack = OriginationStack(name=f"{rel_name}_bootstrap")
            # STUB: Add bootstrap validation for this relationship
            # rel_stack.add_triple(IsA(rel_name, "relationship"))
            # rel_stack.add_triple(PartOf("semantic_logic", rel_name))
            # ... complete bootstrap chain
            
            rel_entity = OntologyEntity(
                name=rel_name,
                origination_stack=rel_stack, 
                entity_type="relationship"
            )
            self.validated_relationships[rel_name] = rel_entity
    
    def register_relationship(self, relationship_name: str, origination_stack: OriginationStack) -> bool:
        """
        STUB: Register new relationship if it has complete OriginationStack.
        
        Pseudocode:
        1. Validate that origination_stack is complete
        2. Check that relationship_name doesn't conflict with existing ones
        3. Verify bootstrap chain includes self-validation
        4. Add to validated_relationships registry
        5. Generate new relationship class dynamically
        6. Return success/failure
        """
        # TODO: Implement full validation
        if not origination_stack.validate_completeness():
            return False
            
        rel_entity = OntologyEntity(
            name=relationship_name,
            origination_stack=origination_stack,
            entity_type="relationship"
        )
        
        if rel_entity.is_instantiable():
            self.validated_relationships[relationship_name] = rel_entity
            return True
        return False
    
    def generate_ontology_for_code(self, code_object) -> List[str]:
        """
        STUB: Generate ontology triples for a code object.
        
        Pseudocode:
        1. AST parse the code object
        2. Extract classes, methods, attributes, imports
        3. Generate is_a relationships (class hierarchy)
        4. Generate part_of relationships (methods/attrs in classes)  
        5. Generate instantiates relationships (object creation)
        6. Use registered relationships to create triples
        7. Return list of ontology triple strings
        """
        ontology_triples = []
        
        # STUB: Simple example for demonstration
        if hasattr(code_object, '__name__'):
            name = code_object.__name__
            
            # Basic type classification
            if hasattr(code_object, '__bases__'):
                # It's a class
                ontology_triples.append(is_a(name, "class"))
                
                # Parent classes
                for base in code_object.__bases__:
                    if base.__name__ != "object":
                        ontology_triples.append(is_a(name, base.__name__))
                
                # Methods and attributes
                for attr_name in dir(code_object):
                    if not attr_name.startswith('_'):
                        attr = getattr(code_object, attr_name)
                        if callable(attr):
                            ontology_triples.append(part_of(attr_name, name, "method"))
                        else:
                            ontology_triples.append(part_of(attr_name, name, "attribute"))
            
            elif callable(code_object):
                # It's a function
                ontology_triples.append(is_a(name, "function"))
        
        return ontology_triples


# Example usage:
if __name__ == "__main__":
    # Create foundational origination stack
    foundational_stack = create_foundational_origination_stack()
    print("Foundational Origination Stack:")
    for triple in foundational_stack.to_triple_strings():
        print(f"  {triple}")
    print(f"Complete: {foundational_stack.validate_completeness()}")
    
    # Create an ontology entity
    document_processor = OntologyEntity(
        name="DocumentProcessor",
        origination_stack=foundational_stack,
        entity_type="class"
    )
    
    print(f"\nDocumentProcessor instantiable: {document_processor.is_instantiable()}")
    print(f"Programs relationship: {document_processor.get_programs_relationship()}")
    
    if document_processor.is_instantiable():
        instance = document_processor.instantiate()
        print(f"Instantiation: {instance}")
    
    # Basic ontological triples
    print(f"\nBasic triples:")
    print(is_a("DocumentProcessor", "Tool"))
    print(part_of("nlp_engine", "DocumentProcessor", "language_processor"))  
    print(instantiates("$my_processor", "DocumentProcessor"))
    print(programs("foundational_bootstrap", "DocumentProcessor"))
    
    # Test ontology generation for a small code stub
    print(f"\n" + "="*50)
    print("ONTOLOGY FOR SMALL CODE EXAMPLE")
    print("="*50)
    
    # Small code stub for testing
    class DocumentProcessor:
        def __init__(self, nlp_engine):
            self.nlp_engine = nlp_engine
            self.processed_count = 0
        
        def process_document(self, text):
            # Simple processing
            return text.upper()
        
        def get_stats(self):
            return {"processed": self.processed_count}
    
    # Generate ontology for the code
    registry = OntologyRegistry()
    ontology_triples = registry.generate_ontology_for_code(DocumentProcessor)
    
    print(f"Generated ontology for DocumentProcessor:")
    for triple in ontology_triples:
        print(f"  {triple}")
    
    # Test with a simple function too
    def process_text(text):
        return text.strip().lower()
    
    function_ontology = registry.generate_ontology_for_code(process_text)
    print(f"\nGenerated ontology for process_text function:")
    for triple in function_ontology:
        print(f"  {triple}")
    
    print(f"\nRegistry has {len(registry.validated_relationships)} registered relationships:")
    for rel_name in registry.validated_relationships.keys():
        print(f"  - {rel_name}")