from random import Random
import random
import string
import modules.scripts as scripts
import gradio as gr
from modules.ui_components import FormRow, FormColumn

from modules import shared
from modules import script_callbacks



class  SdAddRandom2Prompt(scripts.Script):
        
        def __init__(self):
             self.positions = ["start", "end", "anywhere", "random(ly choose one of the options)"]

        # Extension title in menu UI
        def title(self):
                return "add random2prompt"
        def show(self, is_img2img):
                return scripts.AlwaysVisible
        
        def ui(self, is_img2img):
            with gr.Accordion(self.title(), open=False):
                with FormRow():
                    is_enabled = gr.Checkbox(value=getattr(shared.opts, "EnableRandomPromptByDefault", False), label="Enable")
                with FormColumn():
                    length = gr.Slider(label="length of random string", minimum=1, maximum=100, value=getattr(shared.opts, "randomPromptLength", 10), step=1)
                    with FormRow():
                        useLetters = gr.Checkbox(label="use letters", value=True)
                        useNumbers = gr.Checkbox(label="use numbers", value=True)
                        randomStringPosition = gr.Radio(label="where to add in prompt", choices=self.positions, value=self.positions[0])
                    with FormRow():
                        fixed_seed = gr.Checkbox(label="fixed seed", value=getattr(shared.opts, "fixedSeed", True))

                                
                
                return [is_enabled, length, useLetters, useNumbers, randomStringPosition, fixed_seed]

        def process(self, p, is_enabled, length, useLetters, useNumbers, randomStringPosition, fixed_seed):
            if not is_enabled:
                  return
            
            seed = int(p.all_seeds[0])
            
            for i, prompt in enumerate(p.all_prompts):
                    if fixed_seed:
                        p.all_seeds[i] = seed
                    if useLetters and useNumbers:
                        typesToadd = string.ascii_letters + string.digits
                    elif useLetters:
                        typesToadd = string.ascii_letters
                    elif useNumbers:
                        typesToadd = string.digits

                    else:
                         raise ValueError("addRandomToPrompt: no type selected")
                
                    random_string = ''.join(random.choice(typesToadd) for _ in range(length))


                    if randomStringPosition.startswith("random"):
                        randomStringPosition = random.choice(self.positions[:-1])

                    if randomStringPosition == "start":
                        p.all_prompts[i] = f"{random_string}, {prompt}"
                    elif randomStringPosition == "end":
                        p.all_prompts[i] = f"{prompt}, {random_string}"
                    elif randomStringPosition == "anywhere":
                        words = prompt.split()
                        if len(words) < 2:
                             raise ValueError("addRandomToPrompt: prompt is too short to add anywhere")
                        insert_position = random.randint(1, len(words) - 1)
                        words.insert(insert_position, f", {random_string}, ")
                        p.all_prompts[i] = " ".join(words)
                         

                    
                    #print(f"addRandomToPrompt: {p.all_prompts[i]} no.{i}")

def on_ui_settings():
    section = ("random2Prompt", "random2Prompt")
    shared.opts.add_option(
        "EnableRandomPromptByDefault",
        shared.OptionInfo(
            False,
            "enable the random prompt extension by default",
            gr.Checkbox,
            section=section)
    )
    shared.opts.add_option(
        "randomPromptLength",
        shared.OptionInfo(
            10,
            "default length of random string",
            gr.Slider,
            {"minimum": 1, "maximum": 100, "step": 1},
            section=section)
    )
    shared.opts.add_option(
        "fixedSeed",
        shared.OptionInfo(
            True,
            "keep the same seed for each image",
            gr.Checkbox,
            section=section)
    )

script_callbacks.on_ui_settings(on_ui_settings)