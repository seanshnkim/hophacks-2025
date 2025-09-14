from manim import *

class LibrariesAndModulesScene(Scene):
    def construct(self):
        # Title
        title = Text("Libraries and Modules in Python").to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Concept 1: Module
        module_title = Text("Module", font_size=36).next_to(title, DOWN, buff=1)
        module_file = Text("math.py", font_size=28).next_to(module_title, DOWN, buff=0.5)
        module_content = Text("Contains Python definitions and statements", font_size=24).next_to(module_file, DOWN, buff=0.5)
        
        self.play(Write(module_title))
        self.play(FadeIn(module_file, shift=DOWN))
        self.play(Write(module_content))
        self.wait(1.5)

        # Concept 2: Library
        library_title = Text("Library", font_size=36).next_to(title, DOWN, buff=1)
        library_box = Rectangle(width=3, height=2, color=BLUE).next_to(library_title, DOWN, buff=0.5)
        library_modules = VGroup(
            Text("math.py", font_size=24),
            Text("random.py", font_size=24),
            Text("os.py", font_size=24)
        ).arrange(DOWN).move_to(library_box.get_center())
        
        self.play(
            Transform(module_title, library_title),
            FadeOut(module_file),
            FadeOut(module_content),
            Create(library_box),
            Write(library_modules)
        )
        self.wait(1.5)

        # Concept 3: Importing
        import_title = Text("Importing", font_size=36).next_to(title, DOWN, buff=1)
        import_statement = Text("import math", font_size=28).next_to(import_title, DOWN, buff=0.5)
        
        script_box = Rectangle(width=4, height=3, color=GREEN).next_to(import_statement, DOWN, buff=1)
        script_label = Text("Your Script", font_size=24).next_to(script_box, UP)
        
        # Show the import process
        imported_module_copy = VGroup(
            Text("math.py", font_size=24),
            Text("sqrt()", font_size=20)
        ).arrange(DOWN).scale(0.8).move_to(script_box.get_center())

        self.play(
            Transform(library_title, import_title),
            FadeOut(library_box),
            FadeOut(library_modules),
            Write(import_statement),
            Create(script_box),
            Write(script_label)
        )
        self.wait(1)
        
        # Animate the import
        arrow = Arrow(start=import_statement.get_bottom(), end=script_box.get_top(), buff=0.2)
        self.play(Create(arrow))
        self.play(FadeOut(import_statement), FadeOut(arrow))
        self.play(Write(imported_module_copy))
        self.wait(2)

        # Example Usage
        usage_title = Text("Usage Example:", font_size=30).to_edge(LEFT).shift(UP*2)
        usage_code = Text("print(math.sqrt(16))", font_size=28).next_to(usage_title, DOWN, aligned_edge=LEFT)
        result = Text("Result: 4.0", font_size=28).next_to(usage_code, DOWN, aligned_edge=LEFT)

        self.play(Write(usage_title))
        self.play(Write(usage_code))
        self.wait(1)
        self.play(Write(result))
        self.wait(2)
