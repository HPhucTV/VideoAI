#!/usr/bin/env python3
"""
Calibrate all 104 scene prompts for "AI Agent Là Gì?" (Video 92a3ff94-c592-4910-b2c2-facbb2754132):
- Selective 3D screen enlargement: Only in demo/comparison/diagram scenes does the screen occupy 70% of the frame with high contrast UI.
- All other shots feature varied cinematic camera angles: character close-ups, reaction shots, wide lab shots, vector vault, security shield, hero poses.
- Submits batch GENERATE_IMAGE requests to FlowKit.
"""
import sqlite3
import sys
import json
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VIDEO_ID = "92a3ff94-c592-4910-b2c2-facbb2754132"
PROJECT_ID = "bdfe9e57-635b-4036-8a48-c7841a74e208"
AGENT_URL = "http://127.0.0.1:8100"

# Shot specifications based on STORYBOARD_SPEC_104_SHOTS.md
# We classify each shot as either 'screen_demo' (screen prominent 70%) or 'cinematic_character' (focus on character / environment)
SHOT_PROMPTS = {
    # HỒI 1 - CHƯƠNG 1: HOOK (001 - 010)
    1: {
        "type": "cinematic_env",
        "image": "Cinematic wide establishing shot of miniature cyber lab diorama, cute Cyber-Chibi 3D robot Byte floating gracefully into the room, soft cyan neon lights, miniature server racks with glowing pastel lights, clean navy tech floor, 8k render, Octane render aesthetic, Unreal Engine 5.",
        "video": "Cinematic slow dolly-in crane shot, cute Cyber-Chibi robot Byte floating into the high-tech miniature laboratory, soft ambient lighting, subtle blinking LED eyes, 4K composition."
    },
    2: {
        "type": "screen_demo",
        "image": "Cinematic medium over-the-shoulder shot, looking past cute Cyber-Chibi robot Byte at a large floating 3D holographic display occupying 70% of the frame, showing multiple open windows, high contrast glassmorphism, glowing cyan accents, 8k render.",
        "video": "Medium OTS shot, camera gently drifting forward over Byte's shoulder toward the large floating 3D screen, glowing tech particles."
    },
    3: {
        "type": "screen_demo",
        "image": "Macro focus on large 3D holographic display occupying 75% of frame, chaotic multiple browser windows, complex documentation pages and terminal open simultaneously, razor-sharp high contrast typography, dark navy background, cyan and orange UI elements, 8k render.",
        "video": "Macro slow zoom into the 3D screen interface, browser tabs and terminal windows gently hovering in layered depth."
    },
    4: {
        "type": "cinematic_char",
        "image": "Cinematic medium close-up reaction shot, cute Cyber-Chibi robot Byte shaking head sympathetically, expressive blue LED eyes showing tired cross marks, tiny robotic hands gesturing weary sigh, warm studio rim light, Octane Render 8K.",
        "video": "Medium close-up shot, cute Cyber-Chibi Byte gently shaking head with tired expression, LED eyes flickering soft blue, smooth character motion."
    },
    5: {
        "type": "cinematic_env",
        "image": "Dynamic low-angle shot in miniature cyber lab, camera pushing in toward a glowing central tech console, cute Cyber-Chibi Byte floating with mini jetpack glowing bright cyan, dramatic volumetric god rays, 8k render.",
        "video": "Dynamic push-in dolly shot toward central console, vibrant energy sparks swirling as Byte ascends smoothly, cinematic lighting."
    },
    6: {
        "type": "screen_demo",
        "image": "Cinematic shot of large floating 3D screen occupying 70% of frame, autonomous browser automatically navigating, automated scripts extracting data cleanly, glowing neon cyan outlines, high contrast glassmorphism, 8k render.",
        "video": "Screen focus shot, automated browser windows opening smoothly, glowing cursor executing search tasks with fluid animations."
    },
    7: {
        "type": "cinematic_char",
        "image": "Cinematic low-angle hero shot, cute Cyber-Chibi robot Byte smiling proudly with glowing expressive cyan LED eyes, tiny rocket jetpack emitting soft cyan neon smoke rings, miniature lab background with floating bokeh particles, 8k render.",
        "video": "Hero zoom-in punch, Cyber-Chibi Byte smiling proudly as mini jetpack glows with cyan neon energy, speaking with lively mouth movement and bright blue LED eyes."
    },
    8: {
        "type": "screen_demo",
        "image": "Cinematic shot in high-tech lab, magnificent 3D holographic text 'AI AGENT' floating in midair occupying 70% of the frame, luminous electric gold and cyan typography, floating geometric grid lines, Octane render 8K.",
        "video": "Slow tilt up shot, magnificent 3D glowing text 'AI AGENT' materializing with radiant light rays in the center of the virtual laboratory."
    },
    9: {
        "type": "cinematic_char",
        "image": "Cinematic medium shot, cute Cyber-Chibi robot Byte waving friendly robotic hand at the camera, joyful crescent-shaped glowing LED eyes, warm cheerful studio lighting, miniature lab diorama, 8k render.",
        "video": "Medium shot, cute Byte waving cheerfully at the viewer with cute metallic hand, joyful eye expressions, welcoming head tilt."
    },
    10: {
        "type": "cinematic_env",
        "image": "Cinematic pull-back wide shot of miniature high-tech lab diorama, cute Byte hovering beside central workstation, stylish channel branding hologram 'GIẢI MÃ TECH' glowing on the background screen, clean aesthetic, 8k render.",
        "video": "Smooth pull-back dolly shot revealing the grand miniature cyber lab, glowing branding visuals, professional tech documentary look."
    },

    # HỒI 1 - CHƯƠNG 2: CHATBOT VS AI AGENT (011 - 025)
    11: {
        "type": "screen_demo",
        "image": "Cinematic split composition on large 3D floating display occupying 70% of frame: Left side glowing crimson red representing passive chatbot, Right side glowing vibrant cyan representing active autonomous agent, high contrast glassmorphism, 8k render.",
        "video": "Split screen 3D reveal, red and cyan energy halves contrasting vividly with dynamic pulse lines."
    },
    12: {
        "type": "screen_demo",
        "image": "Close-up on left section of 3D display: An adorable retro vintage computer mascot trapped helplessly inside a glowing glass bubble with static text prompt 'Explain Docker', soft red tint, high contrast, 8k render.",
        "video": "Slow dolly-in toward the trapped retro mascot in the glass bubble, static text cursor blinking slowly."
    },
    13: {
        "type": "screen_demo",
        "image": "Macro focus on chat interface on screen: A massive dense block of plain text generated inside a chat bubble, completely static, no external actions, high contrast dark mode UI, 8k render.",
        "video": "Macro shot, long text paragraphs scrolling rapidly inside a static chat bubble without any external tool activation."
    },
    14: {
        "type": "cinematic_char",
        "image": "Cinematic medium shot, cute Cyber-Chibi robot Byte standing with arms crossed, tilting head quizzically with curious yellow LED eyes, observing the static chatbot bubble, warm studio lighting, 8k render.",
        "video": "Medium shot, Byte tilting head curiously, tapping robotic chin thoughtfully, subtle expressive LED eye animations."
    },
    15: {
        "type": "screen_demo",
        "image": "Large 3D floating typography on screen occupying 70% of frame: Bold illuminated text 'HỎI GÌ ĐÁP NẤY = THỤ ĐỘNG' in crisp amber-orange glassmorphism, dark navy background, high contrast, 8k render.",
        "video": "Slow push-in toward the bold floating typography, amber lighting casting soft glow across the lab."
    },
    16: {
        "type": "cinematic_env",
        "image": "Smooth pan shot moving across the high-tech lab to the right, transition from red lighting to brilliant electric cyan and gold aura, cute Byte floating along, 8k render.",
        "video": "Camera panning smoothly from left to right, transitioning atmosphere from dim red to brilliant high-tech cyan."
    },
    17: {
        "type": "screen_demo",
        "image": "Large 3D holographic screen occupying 70% of frame, displaying complex prompt: 'Research Docker, extract 5 key concepts, save to Markdown file', ultra-sharp glowing cyan typography, glassmorphism UI, 8k render.",
        "video": "Screen focus, prompt text typing out rapidly in glowing cyan letters with energetic soundwave visualizer below."
    },
    18: {
        "type": "screen_demo",
        "image": "Large 3D holographic display occupying 75% of frame, splitting into 3 dynamic floating tool windows: Web Scanner with active radar, Data Filter with sorting nodes, and Markdown Writer editor, glowing cyan, 8k render.",
        "video": "Dynamic 3D window expansion, three tool interfaces fanning out smoothly in midair with glowing connecting laser links."
    },
    19: {
        "type": "cinematic_char",
        "image": "Cinematic medium over-the-shoulder shot, cute Cyber-Chibi robot Byte gesturing with metallic fingertips like an orchestra conductor, manipulating glowing floating windows in midair, 8k render.",
        "video": "Medium OTS shot, Byte's cute hands swiping gracefully through holographic light particles, steering data streams."
    },
    20: {
        "type": "screen_demo",
        "image": "Macro bold typography floating on 3D screen occupying 70% of frame: 'TRẢ LỜI CÂU HỎI ≠ ĐIỀU PHỐI NHIỆM VỤ', radiant white and electric cyan high-contrast font, 8k render.",
        "video": "Dramatic camera push-in on the bold contrast statement, light streaks shimmering across the glass letters."
    },
    21: {
        "type": "cinematic_char",
        "image": "Cinematic medium wide shot, cute Cyber-Chibi robot Byte standing between the two paradigms, gesturing outward with both hands in clear comparison, studio lighting, 8k render.",
        "video": "Medium wide shot, Byte gesturing left then right, explaining the fundamental distinction with engaging robotic body language."
    },
    22: {
        "type": "cinematic_char",
        "image": "Low-angle heroic shot, cute Cyber-Chibi robot Byte giving an enthusiastic thumbs-up, bright confident blue LED eyes, miniature tech lab background, 8k render.",
        "video": "Low-angle zoom punch, Byte giving a decisive thumbs-up, joyful energetic facial expression, glowing jetpack pulse."
    },
    23: {
        "type": "screen_demo",
        "image": "Close-up on 3D floating screen occupying 70% of frame, an animated futuristic Task Progress Bar surging smoothly from 0% to 100% with glowing green checkmarks, high contrast UI, 8k render.",
        "video": "Screen focus, task progress bar filling up with glowing emerald green light, accompanied by crisp success indicators."
    },
    24: {
        "type": "cinematic_char",
        "image": "Cinematic 180-degree orbit shot moving around cute Cyber-Chibi robot Byte, admiring the completed workflow with proud glowing eyes, miniature diorama lab, 8k render.",
        "video": "Smooth 180-degree circular camera rotation around Byte, volumetric rim light glistening on sleek metallic surfaces."
    },
    25: {
        "type": "cinematic_char",
        "image": "Cinematic close-up, cute Cyber-Chibi robot Byte holding a glowing translucent data cube in metallic hands, preparing to reveal the inner architecture, Octane Render 8K.",
        "video": "Close-up dolly-in, the glowing data cube in Byte's hands starting to unfold into intricate holographic layers."
    },

    # HỒI 2 - CHƯƠNG 3: BA TRỤ CỘT KIẾN TRÚC (026 - 045)
    26: {
        "type": "screen_demo",
        "image": "Cinematic wide shot, large 3D architectural blueprint flowchart exploding in midair occupying 75% of lab, three major glowing pillar modules: LLM Brain, Instructions, Tools, high contrast glassmorphism, 8k render.",
        "video": "Grand architectural reveal, the 3D flowchart diagram expanding dynamically across the entire laboratory space."
    },
    27: {
        "type": "cinematic_char",
        "image": "Cinematic medium OTS shot, cute Cyber-Chibi robot Byte pointing mini metallic arm toward a glowing violet neural orb floating at the center of the lab, 8k render.",
        "video": "Medium OTS shot, Byte pointing toward the radiant violet orb, camera tilting slightly up to emphasize scale."
    },
    28: {
        "type": "cinematic_env",
        "image": "Cinematic macro shot of the floating translucent purple neural network sphere, pulsating intricate glowing synapses with holographic text 'LLM Brain', quantum light particles, Octane Render 8K.",
        "video": "Macro orbit shot around the purple neural orb, glowing synaptical firings rippling across its translucent core."
    },
    29: {
        "type": "cinematic_env",
        "image": "Ethereal shot of the neural sphere rotating slowly, absorbing streams of binary data and glowing text tokens, deep cosmic navy background, 8k render.",
        "video": "Smooth rotation of the LLM neural sphere, glowing data particles spiraling inward in seamless harmony."
    },
    30: {
        "type": "cinematic_char",
        "image": "Extreme close-up on cute Cyber-Chibi robot Byte's expressive LED eyes, glowing deep intelligent blue with animated neural circuits reflecting logic processing, 8k render.",
        "video": "Extreme macro push-in on Byte's eyes, micro-circuits gently pulsating with thought and intelligence."
    },
    31: {
        "type": "screen_demo",
        "image": "Large 3D holographic display occupying 70% of frame, a radiant amber-gold ring barrier forming around the neural core, labeled 'INSTRUCTIONS & GUARDRAILS', high contrast protective boundary, 8k render.",
        "video": "Screen animation, glowing golden barrier rings interlocking tightly around the central core to illustrate safety boundaries."
    },
    32: {
        "type": "screen_demo",
        "image": "Macro focus on glowing glass boundary ring on screen occupying 70% of frame, illuminated text 'MISSION OBJECTIVES & SAFETY LIMITS' in bold sharp typography, 8k render.",
        "video": "Macro panning along the golden guardrail ring, highlighting the mission parameters and safety boundaries."
    },
    33: {
        "type": "cinematic_char",
        "image": "Cinematic medium close-up, cute Cyber-Chibi robot Byte making a firm X-gesture with metallic arms, determined warning expression, bright amber eye highlight, 8k render.",
        "video": "Medium close-up, Byte crossing arms in firm X gesture, emphasizing strict boundary rules with expressive body language."
    },
    34: {
        "type": "cinematic_char",
        "image": "Cinematic dolly-out shot, three sleek miniature robotic manipulator arms extending from side racks, each holding glowing holographic tool badges, 8k render.",
        "video": "Dolly-out shot, mechanical tool arms extending smoothly into the frame, presenting various capabilities."
    },
    35: {
        "type": "screen_demo",
        "image": "Large 3D floating display occupying 70% of frame, three prominent glowing 3D tool icons: Browser Globe, Terminal Console prompt, and File System folder, high contrast glassmorphism, 8k render.",
        "video": "Screen focus, three tool icons rotating in 3D space with brilliant neon cyan rim lighting."
    },
    36: {
        "type": "screen_demo",
        "image": "Macro focus on 3D code terminal window occupying 70% of frame, glowing Python function definitions 'def web_search()' and 'def write_file()' in vivid syntax highlighting, 8k render.",
        "video": "Macro shot, code lines typing out crisply on dark background with highlighted function names."
    },
    37: {
        "type": "cinematic_char",
        "image": "Cinematic medium shot, cute Cyber-Chibi robot Byte tapping a holographic floating enter key with cheerful curiosity, miniature lab diorama, 8k render.",
        "video": "Medium shot, Byte pressing floating enter key, tiny blue spark emitting on contact as command executes."
    },
    38: {
        "type": "cinematic_env",
        "image": "Cinematic overhead god's-eye view looking down at the laboratory diorama, all three architectural pillars interconnected by luminous light bridges, 8k render.",
        "video": "Slow overhead crane descent, luminous data streams coursing between the three core modules in geometric balance."
    },
    39: {
        "type": "cinematic_env",
        "image": "Cinematic shot inside the ethereal Vector Vault, cute Cyber-Chibi robot Byte floating among towering crystalline memory cubes glowing in soft cyan and amber, cosmic digital space, 8k render.",
        "video": "Ethereal camera sweep through the Vector Vault, translucent memory crystals reflecting laser data highways."
    },
    40: {
        "type": "screen_demo",
        "image": "Large 3D holographic display occupying 70% of frame, displaying 'HUMAN-IN-THE-LOOP' approval checkpoint gate with a glowing handprint verification icon, high contrast UI, 8k render.",
        "video": "Screen focus, human checkpoint gate pulsing gently with amber security beacon and verification scanner."
    },
    41: {
        "type": "screen_demo",
        "image": "Macro warning panel on 3D screen occupying 70% of frame: Bold illuminated text 'LLM DOES NOT OWN TOOLS BY DEFAULT', high contrast technical warning style, dark navy background, 8k render.",
        "video": "Macro zoom on technical warning board, soft amber pulse emphasizing the developer responsibility principle."
    },
    42: {
        "type": "cinematic_char",
        "image": "Cinematic medium shot, cute Cyber-Chibi robot Byte nodding wisely with friendly smiling LED eyes, pointing politely at the audience, 8k render.",
        "video": "Medium shot, Byte nodding in agreement, engaging the viewer with warm and respectful demeanor."
    },
    43: {
        "type": "cinematic_env",
        "image": "Cinematic wide shot, lab lighting smoothly shifting into focused demo mode, overhead spotlights illuminating the main workstation desk, 8k render.",
        "video": "Atmospheric lighting change, ambient room lights dimming as high-intensity demo stage lights power on."
    },
    44: {
        "type": "cinematic_char",
        "image": "Cinematic medium OTS shot, cute Cyber-Chibi robot Byte gliding smoothly over to the central command console, preparing for the live test, 8k render.",
        "video": "Medium OTS shot, Byte floating forward to console, metallic hands poised above the holographic interface."
    },
    45: {
        "type": "cinematic_env",
        "image": "Dynamic fast dolly-in shot zooming into the center of the command console, energetic cyan light tunnel effect leading into Docker demo, 8k render.",
        "video": "Fast forward dolly zoom into the glowing console, bursting with tech enthusiasm as the demo begins."
    },

    # HỒI 3 - CHƯƠNG 4: DEMO DOCKER THỰC TẾ (046 - 065) - MÀN HÌNH MỞ TO 70-75%
    46: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, showing VS Code editor, clean Linux terminal, and official Docker blue whale mascot logo, ultra-sharp readable UI, high contrast glassmorphism, 8k render.",
        "video": "Slow dolly-in toward the massive 3D screen showing the clean developer setup with Docker logo."
    },
    47: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, prominent prompt text typing: 'Research Docker from official docs, export docker-basics.md', crystal clear typography, 8k render.",
        "video": "Screen focus, prompt text typing smoothly character by character in glowing cyan font."
    },
    48: {
        "type": "cinematic_char",
        "image": "Cinematic medium OTS shot, cute Cyber-Chibi robot Byte hovering at lower left corner, raising both metallic hands to initiate the autonomous workflow, 8k render.",
        "video": "Medium OTS shot, Byte gesturing with tiny robotic hands, triggering glowing data stream toward the screen."
    },
    49: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, Thought Process window opening with title 'Step 1: Locate Official Docs at docs.docker.com', ultra-sharp UI, 8k render.",
        "video": "Screen focus, thought process card sliding in with animated tree diagram breaking down the objective."
    },
    50: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, automated Chromium browser window launching, URL bar typing 'https://docs.docker.com/get-started/', 8k render.",
        "video": "Screen focus, browser launching with smooth window animation, navigating directly to Docker Get-Started page."
    },
    51: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, macro view of official web page header 'Docker Docs - Get Started', crisp readable text, high contrast, 8k render.",
        "video": "Macro pan across the Docker documentation page, clean text and official diagrams highlighted."
    },
    52: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, glowing cyan laser scanner line sweeping down the web documentation, highlighting key paragraphs, 8k render.",
        "video": "Screen focus, cyan scanline gliding down the document, extracting raw text with glowing data particle effect."
    },
    53: {
        "type": "cinematic_char",
        "image": "Cinematic close-up, cute Cyber-Chibi robot Byte with glowing LED eyes flashing 'READING...' in animated pixels, tilting head with enthusiastic smile, 8k render.",
        "video": "Close-up shot, Byte's LED eyes animating with scanning graphics, tiny robotic head bobbing in delight."
    },
    54: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, 5 neat floating concept cards appearing: Container, Image, Dockerfile, Volume, Compose, glowing cyan rims, 8k render.",
        "video": "Screen focus, five concept cards cascading into a neat 3D grid with smooth spring physics."
    },
    55: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, zoom into card 'Container': Concise definition with glowing official reference link anchor, ultra-sharp text, 8k render.",
        "video": "Macro focus zooming onto Container card, highlighting verified citation link with green checkmark."
    },
    56: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, text editor window opening, cursor typing Markdown code at blazing speed, high contrast dark theme, 8k render.",
        "video": "Screen focus, Markdown document populating rapidly with headers, bullet points, and code blocks."
    },
    57: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, beautifully formatted Markdown file 'docker-basics.md' with colorful syntax tags and summary comparison table, 8k render.",
        "video": "Screen focus, smooth vertical scroll showcasing the elegant structure of the completed markdown report."
    },
    58: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, terminal confirmation line: '[SUCCESS] File saved: docker-basics.md (4.2 KB)', emerald green text, 8k render.",
        "video": "Screen focus, terminal command prompt executing validation check and displaying green success status."
    },
    59: {
        "type": "cinematic_char",
        "image": "Cinematic medium OTS shot, cute Cyber-Chibi robot Byte flying up close to inspect the generated document with a tiny holographic magnifying glass, 8k render.",
        "video": "Medium OTS shot, Byte hovering close to the screen, meticulously verifying citations and facts."
    },
    60: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, clicking verified link, side popup displaying exact verbatim paragraph from official Docker docs, 8k render.",
        "video": "Screen focus, citation link clicked, original web source paragraph highlighted in golden verification box."
    },
    61: {
        "type": "screen_demo",
        "image": "In the virtual high-tech lab, large floating 3D holographic display occupying 75% of the frame, side-by-side comparison: Generated Markdown on left, Official Docker Documentation on right, 100% matched, 8k render.",
        "video": "Screen focus, dual-pane alignment showing zero hallucinations and 100% accurate information match."
    },
    62: {
        "type": "cinematic_char",
        "image": "Cinematic medium close-up, cute Cyber-Chibi robot Byte tapping a bright glowing green 'VERIFIED' button, joyful triumphant smile, 8k render.",
        "video": "Medium close-up, Byte firmly pressing green VERIFIED button, celebratory emerald light bursting softly."
    },
    63: {
        "type": "cinematic_env",
        "image": "Cinematic wide shot of lab diorama, all demo windows neatly tiling and fading into background, cute Byte hovering happily in center, 8k render.",
        "video": "Wide camera pull-back, windows neatly minimizing into sleek desktop shelf, Byte celebrating demo success."
    },
    64: {
        "type": "cinematic_char",
        "image": "Cinematic medium shot, cute Cyber-Chibi robot Byte turning toward camera, gesturing downward to introduce the underlying mechanism, 8k render.",
        "video": "Medium shot, Byte speaking directly to viewer with expressive robotic hand gestures."
    },
    65: {
        "type": "cinematic_env",
        "image": "Cinematic transition shot, command console surface transforming into a glowing circular loop track with neon cyan energy pulses, 8k render.",
        "video": "Dynamic transformation shot, flat console morphing into an animated three-dimensional orbital ring."
    },

    # HỒI 3 - CHƯƠNG 5: VÒNG LẶP VẬN HÀNH (066 - 077)
    66: {
        "type": "screen_demo",
        "image": "Large 3D holographic display occupying 70% of frame, an elegant 4-stage circular loop track glowing with neon cyan and gold: Input -> Reasoning -> Tool -> Observation, high contrast UI, 8k render.",
        "video": "Screen focus, glowing energy bead traveling smoothly along the 4-stage circular path."
    },
    67: {
        "type": "screen_demo",
        "image": "Macro focus on Stage 1 node on screen occupying 70% of frame: 'Step 1: Input & Context' glowing brightly in cyan neon with incoming task packet, 8k render.",
        "video": "Macro shot, Step 1 node illuminating with bright light as user prompt packet enters the cycle."
    },
    68: {
        "type": "screen_demo",
        "image": "Macro focus on Stage 2 node on screen occupying 70% of frame: 'Step 2: LLM Reasoning' pulsating with violet neural energy, deciding action path, 8k render.",
        "video": "Macro shot, Step 2 node firing synaptical sparks, evaluating whether to answer directly or invoke a tool."
    },
    69: {
        "type": "screen_demo",
        "image": "Macro focus on Stage 3 node on screen occupying 70% of frame: 'Step 3: Tool Execution' branching into API call and capturing response, 8k render.",
        "video": "Macro shot, Step 3 node dispatching rapid data pulse to external tool and receiving clean payload."
    },
    70: {
        "type": "screen_demo",
        "image": "Macro focus on Stage 4 node on screen occupying 70% of frame: 'Step 4: Observation & Decision' feeding output back to the brain, 8k render.",
        "video": "Macro shot, observation data streaming back into the decision loop to confirm task completion."
    },
    71: {
        "type": "screen_demo",
        "image": "Dynamic wide view of 3D loop on screen occupying 70% of frame, energy pulses racing around the closed circuit with rapid tempo and fluid trails, 8k render.",
        "video": "Dynamic pulse animation, loop cycling swiftly through multiple iterations until goal condition is satisfied."
    },
    72: {
        "type": "screen_demo",
        "image": "Large 3D holographic screen occupying 70% of frame, a solid amber-orange security gate descending to halt the loop: 'HUMAN APPROVAL GATE', high contrast, 8k render.",
        "video": "Screen animation, protective barrier locking into place across the loop track with warning indicator."
    },
    73: {
        "type": "cinematic_char",
        "image": "Cinematic medium shot, cute Cyber-Chibi robot Byte standing attentively before the barrier gate, patiently waiting for user confirmation, 8k render.",
        "video": "Medium shot, Byte waiting calmly with hands folded, eyes in polite awaiting mode."
    },
    74: {
        "type": "screen_demo",
        "image": "Macro warning panel on 3D screen occupying 70% of frame: 'LOOP FAILURE RISK: Tool Error / Infinite Recursion', bold orange and red alert UI, 8k render.",
        "video": "Macro focus on risk panel, displaying error telemetry and recursive loop prevention safeguards."
    },
    75: {
        "type": "screen_demo",
        "image": "Macro telemetry readout on screen occupying 70% of frame: 'Max Step Limit: 4/10 Steps' counter and prominent emergency Kill Switch button, 8k render.",
        "video": "Macro shot, digital step counter incrementing cleanly, emergency stop mechanism highlighted in red."
    },
    76: {
        "type": "cinematic_char",
        "image": "Cinematic medium wide shot, cute Cyber-Chibi robot Byte inspecting a row of safety gauges and circuit breakers in the lab diorama, 8k render.",
        "video": "Medium wide shot, Byte checking dials and safety toggles with professional engineering rigor."
    },
    77: {
        "type": "cinematic_env",
        "image": "Cinematic atmospheric transition, lab lighting shifting to warm amber security tone, preparing to discuss real-world constraints, 8k render.",
        "video": "Atmospheric lighting transition from cool cyan to serious warm amber tones."
    },

    # HỒI 4 - CHƯƠNG 6: ỨNG DỤNG & BẢO MẬT (078 - 090)
    78: {
        "type": "screen_demo",
        "image": "Large 3D holographic showcase occupying 70% of frame, unfurling three grand panels representing top three practical AI Agent applications, high contrast UI, 8k render.",
        "video": "Grand reveal, three application showcases expanding horizontally across the virtual lab."
    },
    79: {
        "type": "screen_demo",
        "image": "Macro focus on Panel 1 on screen occupying 70% of frame: AI Coding Assistant reading codebase, fixing syntax error, and running unit tests green, 8k render.",
        "video": "Screen focus, IDE running automated test suite with passing green checkmarks."
    },
    80: {
        "type": "screen_demo",
        "image": "Macro focus on Panel 2 on screen occupying 70% of frame: Deep Research agent parsing dozens of technical papers and creating structured synthesis, 8k render.",
        "video": "Screen focus, multiple PDF research papers being indexed into a clean comparative table."
    },
    81: {
        "type": "screen_demo",
        "image": "Macro focus on Panel 3 on screen occupying 70% of frame: Operations workflow connecting database query, customer email, and CRM update seamlessly, 8k render.",
        "video": "Screen focus, animated pipeline moving customer data between database, mail server, and CRM."
    },
    82: {
        "type": "cinematic_env",
        "image": "Cinematic dramatic lighting shift, lab diorama suddenly bathed in high-contrast amber and crimson warning glow, emphasizing critical security stakes, 8k render.",
        "video": "Dramatic lighting shift, lab alarms pulsing with amber glow, cinematic tech thriller atmosphere."
    },
    83: {
        "type": "screen_demo",
        "image": "Large 3D screen occupying 70% of frame, flashing high-risk terminal command simulation: 'rm -rf / --no-preserve-root', vivid red hazard stripes, 8k render.",
        "video": "Screen focus, terminal command flashing red hazard alert with skull and crossbones safety symbol."
    },
    84: {
        "type": "cinematic_char",
        "image": "Cinematic medium OTS shot, cute Cyber-Chibi robot Byte jumping back in shock as a luminous hexagonal emerald energy shield springs up to protect server, 8k render.",
        "video": "Medium OTS shot, Byte recoiling protectively as emerald force field barrier flares up instantly."
    },
    85: {
        "type": "screen_demo",
        "image": "Macro focus on 3D floating security shield occupying 70% of frame, embossed with glowing gold text: 'PRINCIPLE OF LEAST PRIVILEGE', high contrast, 8k render.",
        "video": "Macro shot, golden security shield rotating with radiant protective energy."
    },
    86: {
        "type": "screen_demo",
        "image": "Large 3D screen occupying 70% of frame, displaying modal dialog: 'CRITICAL PERMISSION REQUIRED: Allow database purge? [YES / NO]', high contrast UI, 8k render.",
        "video": "Screen focus, permission confirmation dialog pulsing with user authorization countdown."
    },
    87: {
        "type": "cinematic_char",
        "image": "Cinematic close-up on cute Cyber-Chibi robot Byte, determined nod, LED eyes displaying a tiny glowing padlock icon, 8k render.",
        "video": "Close-up shot, Byte nodding with steadfast conviction, padlock eye symbol glowing bright cyan."
    },
    88: {
        "type": "cinematic_env",
        "image": "Cinematic wide shot, lab atmosphere returning to serene navy and cyan equilibrium, servers humming quietly in stable security state, 8k render.",
        "video": "Wide camera drift, peaceful lighting restoring calm order to the miniature laboratory."
    },
    89: {
        "type": "cinematic_char",
        "image": "Cinematic medium shot, cute Cyber-Chibi robot Byte speaking to audience with sincere hand-on-chest gesture, miniature diorama lab, 8k render.",
        "video": "Medium shot, Byte sharing architectural wisdom with sincere, articulate gestures."
    },
    90: {
        "type": "cinematic_char",
        "image": "Cinematic medium shot, cute Cyber-Chibi robot Byte gesturing toward the next display board with enthusiastic guiding arm, 8k render.",
        "video": "Medium shot, Byte gesturing toward the decision board, smooth robotic movement."
    },

    # HỒI 4 - CHƯƠNG 7: MA TRẬN QUYẾT ĐỊNH (091 - 098)
    91: {
        "type": "screen_demo",
        "image": "Large 3D holographic decision matrix board occupying 70% of frame, prominent bold title: 'KHI NÀO NÊN DÙNG AI AGENT?', crisp high contrast typography, 8k render.",
        "video": "Screen focus, decision matrix board activating with illuminated category columns."
    },
    92: {
        "type": "screen_demo",
        "image": "Macro focus on Row 1 of decision matrix occupying 70% of frame: 'Simple text task / FAQ -> Use Single Model Call (LLM)', illuminated in soft white, 8k render.",
        "video": "Screen focus, Row 1 lighting up with straightforward single-call icon."
    },
    93: {
        "type": "screen_demo",
        "image": "Macro focus on Row 2 of decision matrix occupying 70% of frame: 'Fixed step-by-step pipeline -> Use Rule-based Workflow', illuminated in amber, 8k render.",
        "video": "Screen focus, Row 2 highlighting sequential workflow arrows and deterministic code blocks."
    },
    94: {
        "type": "screen_demo",
        "image": "Macro focus on Row 3 of decision matrix occupying 70% of frame: 'Multi-step, open-ended, autonomous error-recovery -> USE AI AGENT', glowing radiant cyan, 8k render.",
        "video": "Screen focus, Row 3 blazing with brilliant cyan light, celebrating true agentic applicability."
    },
    95: {
        "type": "screen_demo",
        "image": "Macro focus on telemetry gauges on screen occupying 70% of frame, dual meters showing Token Cost and Latency rising for complex agent loops, high contrast UI, 8k render.",
        "video": "Macro shot, gauges needle deflecting upward to illustrate cost-benefit engineering tradeoffs."
    },
    96: {
        "type": "screen_demo",
        "image": "Large 3D screen occupying 70% of frame, displaying official Anthropic guideline quote: 'Start with the simplest solution and only add complexity when needed', 8k render.",
        "video": "Screen focus, elegant typography with highlighted keywords on minimalist glass background."
    },
    97: {
        "type": "cinematic_char",
        "image": "Cinematic medium OTS shot, cute Cyber-Chibi robot Byte pointing thoughtfully at the Anthropic engineering quote, 8k render.",
        "video": "Medium OTS shot, Byte nodding in deep agreement with the quote, hands gesturing insight."
    },
    98: {
        "type": "cinematic_char",
        "image": "Cinematic medium wide shot, cute Cyber-Chibi robot Byte clapping tiny metallic hands with joyful satisfaction, lab diorama glowing warm, 8k render.",
        "video": "Medium wide shot, Byte clapping hands cheerfully, celebrating practical engineering wisdom."
    },

    # HỒI 5 - CHƯƠNG 8: TỔNG KẾT & TEASER (099 - 104)
    99: {
        "type": "cinematic_char",
        "image": "Cinematic low-angle hero shot, cute Cyber-Chibi robot Byte standing at center of miniature laboratory, arms wide open embracing the future, glorious lighting, 8k render.",
        "video": "Hero crane shot ascending gracefully as Byte welcomes the new age of autonomous intelligence."
    },
    100: {
        "type": "screen_demo",
        "image": "Large 3D holographic display occupying 70% of frame, displaying elegant formula: 'LLM Brain + Tools Execution = Autonomous AI Agent', glowing gold and cyan, 8k render.",
        "video": "Screen focus, equation assembling with shimmering light trails and connecting energy nodes."
    },
    101: {
        "type": "cinematic_char",
        "image": "Cinematic medium shot, cute Cyber-Chibi robot Byte pressing a big neon green Play button, launching a miniature robot prototype that starts walking, 8k render.",
        "video": "Medium shot, Byte pressing play button, tiny companion bot springing to life with delight."
    },
    102: {
        "type": "screen_demo",
        "image": "Large 3D screen occupying 70% of frame, exciting teaser card revealing next episode: 'TẬP TIẾP THEO: MCP (MODEL CONTEXT PROTOCOL)', glowing futuristic badge, 8k render.",
        "video": "Screen focus, teaser card rotating in 3D with dramatic light sweep and next episode preview graphics."
    },
    103: {
        "type": "screen_demo",
        "image": "Large 3D screen occupying 70% of frame, animated YouTube Subscribe, Like, and Bell notification buttons exploding with festive cyan and gold confetti, 8k render.",
        "video": "Screen focus, Subscribe button clicking with satisfying spring animation and sparkling particle bursts."
    },
    104: {
        "type": "cinematic_char",
        "image": "Cinematic medium close-up, cute Cyber-Chibi robot Byte waving goodbye warmly to viewer, bright smiling heart-shaped LED eyes, warm ambient bokeh, 8k render.",
        "video": "Medium close-up, Byte waving affectionately goodbye, sweet smiling LED eye animation, camera gently pulling back."
    }
}


def calibrate_scenes_in_db():
    print("=" * 65)
    print("🎯 HIỆU CHỈNH 104 PROMPTS TRONG SQLITE CHO XƯỞNG 4...")
    print("=" * 65)
    conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db')
    c = conn.cursor()

    # Update project_id on video
    c.execute("UPDATE video SET project_id = ? WHERE id = ?", (PROJECT_ID, VIDEO_ID))

    screen_count = 0
    char_count = 0

    for order, spec in SHOT_PROMPTS.items():
        img_prompt = spec["image"]
        vid_prompt = spec["video"]
        shot_type = spec["type"]

        if shot_type == "screen_demo":
            screen_count += 1
            char_names = json.dumps(["Byte", "Viện Công Nghệ Tí Hon"])
        elif order in (38, 39):
            char_names = json.dumps(["Byte", "Kho Lưu Trữ Dữ Liệu Vector"])
        else:
            char_count += 1
            char_names = json.dumps(["Byte", "Viện Công Nghệ Tí Hon"])

        # Reset any stale media ids so real generation happens
        c.execute("""
            UPDATE scene SET 
                image_prompt = ?, 
                video_prompt = ?, 
                character_names = ?,
                horizontal_image_media_id = NULL,
                horizontal_image_url = NULL,
                horizontal_image_status = 'PENDING',
                horizontal_video_media_id = NULL,
                horizontal_video_url = NULL,
                horizontal_video_status = 'PENDING'
            WHERE video_id = ? AND display_order = ?
        """, (img_prompt, vid_prompt, char_names, VIDEO_ID, order))

    conn.commit()
    conn.close()
    print(f"✅ Đã cập nhật xong 104 cảnh trong SQLite!")
    print(f"   - Phân cảnh Màn hình 3D mở to rõ nét (Screen Demo): {screen_count} cảnh")
    print(f"   - Phân cảnh Điện ảnh đa dạng góc máy (Character / Env): {char_count} cảnh")


def submit_batch_requests():
    print("\n" + "=" * 65)
    print("📤 GỬI BATCH 104 YÊU CẦU GENERATE_IMAGE TỚI FLOWKIT DAEMON...")
    print(f"Target Video ID: {VIDEO_ID}")
    print(f"Target Project ID: {PROJECT_ID}")
    print("=" * 65)

    # 1. Clear any old pending/processing requests for this video
    conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db')
    c = conn.cursor()
    c.execute("DELETE FROM request WHERE video_id = ?", (VIDEO_ID,))
    conn.commit()
    conn.close()
    print("[*] Đã dọn dẹp các request cũ cho video này.")

    # 2. Fetch scenes
    r = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
    if r.status_code != 200:
        print(f"[ERR] Không lấy được danh sách scenes: {r.status_code}")
        return False
    scenes = r.json()
    print(f"[*] Đã tải {len(scenes)} cảnh từ FlowKit API.")

    batch_reqs = []
    for s in scenes:
        batch_reqs.append({
            "type": "GENERATE_IMAGE",
            "scene_id": s["id"],
            "project_id": PROJECT_ID,
            "video_id": VIDEO_ID,
            "orientation": "HORIZONTAL"
        })

    print(f"[*] Đang gửi batch gồm {len(batch_reqs)} yêu cầu tới {AGENT_URL}/api/requests/batch...")
    res = requests.post(f"{AGENT_URL}/api/requests/batch", json={"requests": batch_reqs}, timeout=30)
    if res.status_code == 200:
        data = res.json()
        print(f"✅ THÀNH CÔNG: Đã đăng ký {len(data)} yêu cầu sinh ảnh Imagen 3 vào hàng đợi FlowKit!")
        return True
    else:
        print(f"❌ LỖI: Không thể gửi batch request: {res.status_code} - {res.text}")
        return False


if __name__ == "__main__":
    calibrate_scenes_in_db()
    ok = submit_batch_requests()
    if not ok:
        sys.exit(1)
