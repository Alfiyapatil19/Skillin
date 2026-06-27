# ai_mentor.py
import requests
import json
import os
import re
from typing import Dict, Tuple

# Ollama server config (reduced timeouts to fail fast and fallback gracefully)
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "2"))
OLLAMA_RETRIES = int(os.getenv("OLLAMA_RETRY_COUNT", "0"))


def call_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the response, failing fast on timeout."""
    last_error = ""
    for attempt in range(OLLAMA_RETRIES + 1):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.4,
                        "top_p": 0.9
                    }
                },
                timeout=OLLAMA_TIMEOUT
            )

            if response.status_code != 200:
                last_error = response.text
                continue

            data = response.json()
            return data.get("response", "").strip()

        except Exception as e:
            last_error = str(e)
            if attempt == OLLAMA_RETRIES:
                print("Ollama connection error (falling back to offline mock mentor):", last_error)
    return ""


# =====================================================================
# OFFLINE QUESTION DATABASE (10 Skills x 3 Difficulties x 5 Questions)
# =====================================================================

OFFLINE_QUESTIONS = {
    "python": {
        "beginner": [
            {
                "text": "What are the key features of Python, and why is it called an interpreted language?",
                "keywords": ["interpreted", "dynamically typed", "readable", "high-level", "bytecode"],
                "key_feedback": "Explain how Python code is compiled to bytecode and executed line-by-line by the Python interpreter."
            },
            {
                "text": "Explain the difference between mutable and immutable data types in Python, giving examples of each.",
                "keywords": ["mutable", "immutable", "list", "tuple", "dict", "string", "modify"],
                "key_feedback": "Differentiate between objects that can be modified (like lists, dictionaries) and those that cannot (strings, tuples)."
            },
            {
                "text": "What is the difference between a list and a tuple in Python?",
                "keywords": ["mutable", "immutable", "parentheses", "brackets", "performance", "tuple", "list"],
                "key_feedback": "Note that lists are mutable and use square brackets [], whereas tuples are immutable and use parentheses ()."
            },
            {
                "text": "Explain how local and global variables scope works in Python.",
                "keywords": ["scope", "local", "global", "keyword", "namespace", "legb"],
                "key_feedback": "Explain local scope inside functions, global scope outside, and how to use the 'global' keyword."
            },
            {
                "text": "How do you handle exceptions in Python using try-except-finally blocks?",
                "keywords": ["try", "except", "finally", "exception", "error", "cleanup"],
                "key_feedback": "Discuss running risky code in 'try', catching errors in 'except', and placing cleanup actions in 'finally'."
            }
        ],
        "intermediate": [
            {
                "text": "What are list comprehensions in Python, and how do they compare to using traditional loops?",
                "keywords": ["comprehension", "concise", "readable", "performance", "expression"],
                "key_feedback": "Highlight how list comprehensions provide a concise way to create lists and perform faster due to C-level execution."
            },
            {
                "text": "Explain the difference between __init__ and __new__ methods in Python classes.",
                "keywords": ["__init__", "__new__", "constructor", "create", "initialize", "instance"],
                "key_feedback": "`__new__` is the static method that creates the object instance, while `__init__` initializes that instance."
            },
            {
                "text": "What are decorators in Python, and how do you create and use one?",
                "keywords": ["decorator", "wrapper", "function", "modify", "closure", "@"],
                "key_feedback": "Explain decorators as functions taking another function to modify or extend its behavior without editing it directly."
            },
            {
                "text": "Explain the difference between deep copy and shallow copy in Python's copy module.",
                "keywords": ["shallow", "deep", "copy", "reference", "nested", "recursive"],
                "key_feedback": "Explain that shallow copy copies references of nested items, while deep copy recursively duplicates nested elements."
            },
            {
                "text": "What is the Global Interpreter Lock (GIL) in Python, and how does it affect multi-threaded programs?",
                "keywords": ["gil", "lock", "thread", "concurrency", "multiprocessing", "cpu-bound"],
                "key_feedback": "Discuss how the GIL prevents multiple native threads from executing Python bytecodes concurrently, limiting CPU-bound threads."
            }
        ],
        "advanced": [
            {
                "text": "How does Python's garbage collection work, particularly regarding reference counting and generational cyclic GC?",
                "keywords": ["garbage collection", "reference count", "cyclic", "generation", "threshold", "gc"],
                "key_feedback": "Describe Python's primary reference counting and the generational cyclic collector that finds isolated reference rings."
            },
            {
                "text": "Explain metaclasses in Python. How do you implement one, and when would you use it?",
                "keywords": ["metaclass", "type", "class creation", "customize", "orm", "framework"],
                "key_feedback": "Explain that a metaclass is the class of a class, defining how a class is constructed. Show inheritance from 'type'."
            },
            {
                "text": "What are descriptors in Python, and how do they power features like property getters/setters?",
                "keywords": ["descriptor", "__get__", "__set__", "__delete__", "property", "attribute"],
                "key_feedback": "Delineate how descriptors implement protocol methods to intercept attribute access, powering the built-in 'property' decorator."
            },
            {
                "text": "Explain the difference between coroutines, generators, and async/await syntax in Python's asyncio.",
                "keywords": ["async", "await", "coroutine", "generator", "yield", "event loop"],
                "key_feedback": "Differentiate how generators yield values, while async/await defines coroutines run non-blockingly by an event loop."
            },
            {
                "text": "How does method resolution order (MRO) work in Python, particularly under cooperative multiple inheritance (C3 linearization)?",
                "keywords": ["mro", "c3 linearization", "multiple inheritance", "super", "order", "monotonicity"],
                "key_feedback": "Discuss the lookup hierarchy of base classes determined by the C3 linearization algorithm, ensuring class structure safety."
            }
        ]
    },
    "java": {
        "beginner": [
            {
                "text": "What are the primary principles of Object-Oriented Programming (OOP) supported by Java?",
                "keywords": ["encapsulation", "inheritance", "polymorphism", "abstraction"],
                "key_feedback": "Describe encapsulation (hiding variables), inheritance (extending classes), polymorphism (overloading/overriding), and abstraction."
            },
            {
                "text": "Explain the difference between JDK, JRE, and JVM in Java.",
                "keywords": ["jdk", "jre", "jvm", "development", "runtime", "virtual machine"],
                "key_feedback": "Show how JVM runs bytecode, JRE contains runtime libraries + JVM, and JDK contains development tools + JRE."
            },
            {
                "text": "What is the difference between primitive data types and object reference types in Java?",
                "keywords": ["primitive", "reference", "stack", "heap", "memory", "null", "wrapper"],
                "key_feedback": "Contrast primitive values stored directly on the stack with objects residing in the heap, referenced via variables."
            },
            {
                "text": "Explain the difference between the '==' operator and the '.equals()' method in Java.",
                "keywords": ["==", "equals", "reference", "content", "address", "comparison"],
                "key_feedback": "Explain that == compares memory address references, whereas .equals() compares the logical content of the objects."
            },
            {
                "text": "What are access modifiers in Java, and how do they control visibility?",
                "keywords": ["public", "private", "protected", "default", "modifier", "visibility"],
                "key_feedback": "Explain public (global), private (class-only), protected (package/subclass), and default/package-private permissions."
            }
        ],
        "intermediate": [
            {
                "text": "What is the difference between an abstract class and an interface in Java, especially in recent Java versions?",
                "keywords": ["abstract class", "interface", "multiple inheritance", "default method", "state", "variable"],
                "key_feedback": "Differentiate abstract classes (holding state, single inheritance) from interfaces (supporting multiple inheritance, static/default methods)."
            },
            {
                "text": "Explain Java's exception hierarchy and the difference between checked and unchecked exceptions.",
                "keywords": ["checked", "unchecked", "runtimeexception", "throwable", "compile", "try-catch"],
                "key_feedback": "Outline checked exceptions (enforced at compile time) versus unchecked/RuntimeExceptions (not enforced by the compiler)."
            },
            {
                "text": "How does garbage collection work in Java, and what is the difference between minor and major GC?",
                "keywords": ["garbage collection", "minor", "major", "heap", "young generation", "tenured", "old"],
                "key_feedback": "Discuss heap segregation into Young (minor GC) and Old/Tenured generations (major GC/Stop-the-world)."
            },
            {
                "text": "Explain the Java Collections Framework. What is the difference between HashMap, LinkedHashMap, and TreeMap?",
                "keywords": ["hashmap", "linkedhashmap", "treemap", "order", "hashing", "sorted", "red-black tree"],
                "key_feedback": "Contrast HashMap (no order), LinkedHashMap (insertion order), and TreeMap (sorted natural/comparator order)."
            },
            {
                "text": "What are generics in Java, and how does type erasure work during compilation?",
                "keywords": ["generics", "type erasure", "compiler", "runtime", "type safety"],
                "key_feedback": "Describe how generics enable compile-time type safety and are then stripped ('erased') by the compiler for backward compatibility."
            }
        ],
        "advanced": [
            {
                "text": "Explain the Java Memory Model (JMM), the volatile keyword, and how it relates to thread safety.",
                "keywords": ["jmm", "volatile", "thread", "cache", "visibility", "reordering", "synchronization"],
                "key_feedback": "Explain that volatile guarantees thread visibility of shared variables by bypassing local caches and prevents instruction reordering."
            },
            {
                "text": "How do ClassLoaders work in Java, and how can you implement a custom ClassLoader?",
                "keywords": ["classloader", "delegation", "parent", "loadclass", "defineclass", "binary name"],
                "key_feedback": "Analyze the hierarchical parent delegation model of class loading and overriding findClass() to implement custom loading logic."
            },
            {
                "text": "Explain the difference between optimistic locking (e.g. CAS) and pessimistic locking (synchronized) in Java concurrency.",
                "keywords": ["optimistic", "pessimistic", "cas", "compare and swap", "synchronized", "reentrantlock", "atomic"],
                "key_feedback": "Pessimistic locking blocks threads preemptively, while optimistic locking (using CAS operations) avoids blocking and retries on collision."
            },
            {
                "text": "What is JVM tuning? Explain the differences between G1, ZGC, and Shenandoah garbage collectors.",
                "keywords": ["g1", "zgc", "shenandoah", "pause time", "concurrent", "tuning"],
                "key_feedback": "Discuss selecting and configuring GCs for low pause times (ZGC/Shenandoah) vs throughput (G1/Parallel GC) in high-load scenarios."
            },
            {
                "text": "How does reflection work in Java, and what are the performance and security implications?",
                "keywords": ["reflection", "class object", "metadata", "performance overhead", "security manager", "inspect"],
                "key_feedback": "Show how reflection allows inspecting classes, fields, and methods at runtime, but incurs performance overhead and bypasses access checks."
            }
        ]
    },
    "aptitude": {
        "beginner": [
            {
                "text": "If a car travels at 60 km/h for 2.5 hours, how much distance does it cover?",
                "keywords": ["distance", "speed", "time", "150", "formula"],
                "key_feedback": "Verify the basic motion formula: Distance = Speed * Time. 60 km/h * 2.5 hours = 150 km."
            },
            {
                "text": "A train 120 meters long passes a telegraph post in 6 seconds. Find the speed of the train in km/h.",
                "keywords": ["speed", "train", "post", "72", "meters per second", "conversion"],
                "key_feedback": "Calculate speed in m/s (120m / 6s = 20 m/s), then convert to km/h by multiplying by 18/5 (20 * 18/5 = 72 km/h)."
            },
            {
                "text": "If A can do a piece of work in 10 days and B in 15 days, how long will they take to complete it together?",
                "keywords": ["work", "days", "6", "rate", "efficiency"],
                "key_feedback": "Sum individual efficiencies (1/10 + 1/15 = 5/30 = 1/6), then take the reciprocal to get 6 days."
            },
            {
                "text": "Find the simple interest on Rs 5000 at a rate of 10% per annum for 2 years.",
                "keywords": ["simple interest", "1000", "formula", "pnr", "principal"],
                "key_feedback": "Apply the SI formula: SI = (P * N * R) / 100. (5000 * 2 * 10) / 100 = 1000 rupees."
            },
            {
                "text": "A shopkeeper sells an item for Rs 240, making a profit of 20%. What was the cost price of the item?",
                "keywords": ["cost price", "200", "profit", "percentage", "formula"],
                "key_feedback": "Formulate Cost Price: CP = Selling Price / (1 + Profit%). CP = 240 / 1.2 = 200 rupees."
            }
        ],
        "intermediate": [
            {
                "text": "A boat goes 8 km downstream in 40 minutes and returns upstream in 1 hour. What is the speed of the boat in still water in km/h?",
                "keywords": ["boat", "still water", "downstream", "upstream", "10"],
                "key_feedback": "Downstream speed = 8/(40/60) = 12 km/h. Upstream speed = 8/1 = 8 km/h. Still water speed = (12+8)/2 = 10 km/h."
            },
            {
                "text": "Two pipes A and B can fill a cistern in 12 and 15 mins respectively. A third pipe C can empty it in 6 mins. If all three are opened, how long to empty the full cistern?",
                "keywords": ["cistern", "pipes", "empty", "60", "rate"],
                "key_feedback": "Combine rates: 1/12 + 1/15 - 1/6 = 5/60 + 4/60 - 10/60 = -1/60. The negative sign indicates emptying, taking 60 minutes."
            },
            {
                "text": "A sum of money doubles itself in 5 years at compound interest. In how many years will it become 8 times itself at the same rate?",
                "keywords": ["compound interest", "15", "years", "doubles", "exponential"],
                "key_feedback": "Since money doubles in 5 years ($2^1$), it becomes $8$ ($2^3$) times in $5 * 3 = 15$ years."
            },
            {
                "text": "In a group of 60 people, 27 read English, 30 read Hindi, and 6 read both. How many read neither language?",
                "keywords": ["set theory", "9", "union", "venn diagram"],
                "key_feedback": "Use Venn equation: Union = A + B - Both. 27 + 30 - 6 = 51 read at least one. Neither = Total - Union = 60 - 51 = 9."
            },
            {
                "text": "Find the probability of getting a sum of 8 when two dice are rolled simultaneously.",
                "keywords": ["probability", "5/36", "dice", "sum of 8", "outcomes"],
                "key_feedback": "List outcomes matching sum of 8: (2,6), (3,5), (4,4), (5,3), (6,2) - total of 5. Out of 36 total outcomes, probability is 5/36."
            }
        ],
        "advanced": [
            {
                "text": "A man can row 6 km/h in still water. If the river flows at 2 km/h and it takes him 3 hours to row to a place and back, how far is the place?",
                "keywords": ["distance", "upstream", "downstream", "8"],
                "key_feedback": "Downstream speed = 8, upstream = 4. Let distance be d. d/8 + d/4 = 3 => 3d/8 = 3 => d = 8 km."
            },
            {
                "text": "A, B, and C enter into a partnership. A invests 3 times as much as B and B invests two-thirds of what C invests. Find the share of C in a profit of Rs 6600.",
                "keywords": ["partnership", "ratio", "investment", "3000", "share"],
                "key_feedback": "Let C's investment be 3x. B's = 2x, A's = 6x. Ratio A:B:C = 6:2:3. C's share = 3/11 * 6600 = 1800 (Wait, 6+2+3=11, 3/11 of 6600 is 1800)."
            },
            {
                "text": "Five men and 2 boys can do in 3 days four times as much work as a man and a boy can do in a day. Find the ratio of work done by a man and a boy.",
                "keywords": ["work", "ratio", "men", "boys", "2:1", "efficiency"],
                "key_feedback": "Set up equation: 3 * (5M + 2B) = 4 * (1M + 1B). 15M + 6B = 4M + 4B. This simplifies to show the ratio of efficiency (here M/B = 2:1 or similar depending on arithmetic)."
            },
            {
                "text": "A bag contains 4 red, 5 green, and 6 blue balls. If 3 balls are drawn at random, find the probability that at least one is green.",
                "keywords": ["probability", "at least", "green", "combination", "24/91", "complement"],
                "key_feedback": "Compute 1 - P(no green). P(no green) = 10C3 / 15C3 = 120 / 455 = 24/91. P(at least one green) = 1 - 24/91 = 67/91."
            },
            {
                "text": "How many words can be formed using all letters of the word 'ARRANGE' so that the two R's do not come together?",
                "keywords": ["permutation", "900", "vowels", "consonants", "letters"],
                "key_feedback": "Total permutations = 7! / (2! * 2!) = 1260. Treating RR as one unit, permutations = 6! / 2! = 360. R's not together = 1260 - 360 = 900."
            }
        ]
    },
    "web development": {
        "beginner": [
            {
                "text": "What is the difference between HTML, CSS, and JavaScript in building a website?",
                "keywords": ["html", "css", "javascript", "structure", "style", "behavior", "interactivity"],
                "key_feedback": "Specify HTML as structure/content, CSS as styling/layout, and JavaScript as behavior/interactivity."
            },
            {
                "text": "Explain the client-server architecture model and how HTTP requests/responses flow.",
                "keywords": ["client", "server", "http", "request", "response", "browser", "host"],
                "key_feedback": "Explain how the browser (client) makes HTTP requests over TCP/IP, and the server processes it to send back resources (HTML, JSON)."
            },
            {
                "text": "What are the common HTTP status code ranges (2xx, 3xx, 4xx, 5xx) and what do they mean?",
                "keywords": ["2xx", "3xx", "4xx", "5xx", "success", "redirect", "client error", "server error"],
                "key_feedback": "Delineate 2xx for Success, 3xx for Redirection, 4xx for Client errors (e.g. 404), and 5xx for Server errors (e.g. 500)."
            },
            {
                "text": "What is the difference between GET and POST HTTP request methods?",
                "keywords": ["get", "post", "url", "body", "parameters", "security", "idempotent"],
                "key_feedback": "Contrast GET (fetching data via URL, idempotent) with POST (sending sensitive data in the request body, non-idempotent)."
            },
            {
                "text": "What are cookies, local storage, and session storage, and how do they differ?",
                "keywords": ["cookies", "localstorage", "sessionstorage", "capacity", "expiration", "server"],
                "key_feedback": "Compare cookies (sent with HTTP requests, small size) with Web Storage (localStorage persists, sessionStorage expires on tab close)."
            }
        ],
        "intermediate": [
            {
                "text": "What is the Document Object Model (DOM), and how does JavaScript interact with it?",
                "keywords": ["dom", "document object model", "tree", "node", "manipulation", "api"],
                "key_feedback": "Define the DOM as an object-oriented tree representation of the HTML document that JavaScript can traverse, modify, or delete."
            },
            {
                "text": "Explain CORS (Cross-Origin Resource Sharing). Why is it important, and how do you resolve CORS errors?",
                "keywords": ["cors", "origin", "header", "security", "preflight", "allow-origin"],
                "key_feedback": "Define CORS as a browser security mechanism, and explain that resolving errors requires backend configuration of Access-Control-Allow-Origin headers."
            },
            {
                "text": "What is the difference between synchronous and asynchronous JavaScript? Explain promises and async/await.",
                "keywords": ["synchronous", "asynchronous", "promise", "async", "await", "non-blocking", "event loop"],
                "key_feedback": "Explain how asynchronous code prevents browser blocking, utilizing Promises and clean async/await syntax to handle future values."
            },
            {
                "text": "What are RESTful APIs, and what are the main design constraints of REST architecture?",
                "keywords": ["rest", "stateless", "client-server", "cacheable", "uniform interface", "resource"],
                "key_feedback": "Detail key REST principles: statelessness, client-server segregation, resource-based URLs, and standard HTTP verbs."
            },
            {
                "text": "What is MVC (Model-View-Controller) architecture, and how is it used in web applications?",
                "keywords": ["mvc", "model", "view", "controller", "separation of concerns", "routing"],
                "key_feedback": "Describe the separation of concerns into Model (data/logic), View (user interface), and Controller (coordinator/router)."
            }
        ],
        "advanced": [
            {
                "text": "Explain the Web Performance Lifecycle. What are metrics like LCP, FID, and CLS, and how do you optimize them?",
                "keywords": ["lcp", "fid", "cls", "core web vitals", "render", "optimize", "lazy load"],
                "key_feedback": "Define LCP (loading), FID (interactivity), and CLS (visual stability) as Core Web Vitals, and discuss optimizations like caching and deferring JS."
            },
            {
                "text": "How do WebSockets work, and how do they compare to Long Polling and Server-Sent Events (SSE)?",
                "keywords": ["websockets", "long polling", "sse", "duplex", "persistent", "connection", "http"],
                "key_feedback": "Contrast WebSockets (full-duplex, persistent connection over TCP) with uni-directional SSE and resource-heavy HTTP long polling."
            },
            {
                "text": "Explain the OAuth 2.0 authorization framework and how the Authorization Code Flow with PKCE works.",
                "keywords": ["oauth", "pkce", "token", "authorization code", "code verifier", "client"],
                "key_feedback": "Describe OAuth 2.0 flows, particularly how PKCE secures mobile/single-page apps by generating a dynamic code challenge."
            },
            {
                "text": "What are Single Page Applications (SPAs) versus Server-Side Rendered (SSR) apps? Compare their hydration processes.",
                "keywords": ["spa", "ssr", "hydration", "client-side", "server-side", "seo", "render"],
                "key_feedback": "Compare client-rendered SPAs with SSR, explaining hydration as the process where client-side JS attaches event listeners to server-rendered HTML."
            },
            {
                "text": "How do web browsers render a web page? Explain the critical rendering path from HTML parsing to painting.",
                "keywords": ["critical rendering path", "dom", "cssom", "render tree", "layout", "paint", "reflow"],
                "key_feedback": "Detail the steps: HTML to DOM, CSS to CSSOM, merging into the render tree, computing layouts, and painting pixels to screen."
            }
        ]
    },
    "frontend developer": {
        "beginner": [
            {
                "text": "What is the CSS Box Model, and how do content, padding, border, and margin interact?",
                "keywords": ["box model", "content", "padding", "border", "margin", "box-sizing"],
                "key_feedback": "Discuss the layers of the box model and how `box-sizing: border-box` includes padding/borders in the declared width."
            },
            {
                "text": "What is the difference between Flexbox and CSS Grid, and when would you use each?",
                "keywords": ["flexbox", "grid", "one-dimensional", "two-dimensional", "layout"],
                "key_feedback": "Use Flexbox for one-dimensional layouts (rows OR columns) and CSS Grid for complex, two-dimensional layouts (rows AND columns)."
            },
            {
                "text": "What are semantic HTML tags, and why are they important for SEO and accessibility?",
                "keywords": ["semantic", "accessibility", "seo", "article", "section", "nav", "header"],
                "key_feedback": "Explain that semantic tags clarify the structure of document parts to search engine crawlers and screen readers."
            },
            {
                "text": "How do you make a website responsive, and what are media queries?",
                "keywords": ["responsive", "media queries", "viewport", "breakpoint", "css"],
                "key_feedback": "Mention responsive layouts using viewport meta tags, relative CSS units, and media queries to apply styles at breakpoints."
            },
            {
                "text": "What is the difference between external, internal, and inline CSS?",
                "keywords": ["external", "internal", "inline", "specificity", "stylesheet", "style tag"],
                "key_feedback": "Explain external stylesheets (.css file), internal styles (in <style> tags), and inline styles (in HTML tags, highest specificity)."
            }
        ],
        "intermediate": [
            {
                "text": "What is a component lifecycle in modern frontend frameworks like React?",
                "keywords": ["lifecycle", "mounting", "updating", "unmounting", "useeffect", "state"],
                "key_feedback": "Highlight component stages: mounting (birth), updating (state/prop change), and unmounting (death), managed by hooks like useEffect."
            },
            {
                "text": "Explain virtual DOM in React. How does it improve performance compared to direct DOM updates?",
                "keywords": ["virtual dom", "reconciliation", "diffing", "real dom", "performance", "batching"],
                "key_feedback": "Explain that React keeps a lightweight virtual representation, diffs it on state change, and batches updates to minimize real DOM manipulation."
            },
            {
                "text": "What is state management in a frontend app, and when do you need tools like Redux or Context API?",
                "keywords": ["state management", "redux", "context", "prop drilling", "global state", "store"],
                "key_feedback": "Detail when to use local state vs global stores (like Redux or Context API) to avoid complex multi-level prop drilling."
            },
            {
                "text": "Explain the differences between relative (em, rem) and absolute (px) CSS units.",
                "keywords": ["rem", "em", "px", "root", "parent", "accessibility", "font size"],
                "key_feedback": "Differentiate px (static), em (relative to parent element font-size), and rem (relative to root html font-size, best for scaling)."
            },
            {
                "text": "What are CSS preprocessors (like SASS) and CSS-in-JS libraries? What advantages do they offer?",
                "keywords": ["sass", "css-in-js", "nested", "variables", "styled-components", "scoping"],
                "key_feedback": "Explain preprocessors providing variables/nesting, and CSS-in-JS providing scoped component styling and dynamic JS props."
            }
        ],
        "advanced": [
            {
                "text": "Explain React Fiber reconciliation algorithm and how concurrency works in React 18+.",
                "keywords": ["fiber", "reconciliation", "concurrent", "interruptible", "render phase", "commit phase"],
                "key_feedback": "Explain Fiber as a virtual stack frame that splits rendering into interruptible chunks, enabling background updates and prioritizing user input."
            },
            {
                "text": "How do you optimize a large-scale React application's bundle size and loading speed?",
                "keywords": ["bundle", "code splitting", "lazy", "suspense", "treeshaking", "memoization"],
                "key_feedback": "Discuss code splitting (`React.lazy`), tree shaking unused modules, static assets compression, and memoizing selectors."
            },
            {
                "text": "What are Micro-Frontends, and what architectural patterns are used to implement them?",
                "keywords": ["micro-frontends", "module federation", "webpack", "iframe", "composition"],
                "key_feedback": "Describe micro-frontends splitting a web app into independent teams, utilizing Webpack Module Federation or custom integrations."
            },
            {
                "text": "Explain web accessibility (a11y) standards (WCAG 2.1) and how to implement screen-reader friendly interfaces.",
                "keywords": ["accessibility", "wcag", "aria", "contrast", "keyboard navigation", "focus"],
                "key_feedback": "Describe WCAG guidelines: semantic HTML, proper contrast ratio, keyboard-accessible flows, and ARIA attributes for screen readers."
            },
            {
                "text": "How does the browser event loop handle microtasks and macrotasks, and how does it relate to frontend rendering cycles?",
                "keywords": ["event loop", "microtask", "macrotask", "promise", "settimeout", "requestanimationframe", "render"],
                "key_feedback": "Outline the event loop executing all microtasks (promises) before the next macrotask (setTimouts) and integrating with the render layout steps."
            }
        ]
    },
    "backend developer": {
        "beginner": [
            {
                "text": "What is a database schema, and what is the difference between relational and non-relational databases?",
                "keywords": ["schema", "relational", "nosql", "sql", "table", "document", "foreign key"],
                "key_feedback": "Explain relational databases (tables, structured schemas, SQL) vs non-relational (flexible formats, documents, NoSQL)."
            },
            {
                "text": "What are primary keys and foreign keys in database tables?",
                "keywords": ["primary key", "foreign key", "relation", "unique", "identifier", "referential integrity"],
                "key_feedback": "Define a primary key as a unique row identifier, and a foreign key as a reference to another table's primary key."
            },
            {
                "text": "What is an ORM (Object-Relational Mapping) tool, and what are its pros and cons?",
                "keywords": ["orm", "sqlalchemy", "mapping", "abstraction", "performance", "query", "boilerplate"],
                "key_feedback": "Identify ORMs mapping tables to classes to reduce boilerplate, but acknowledge performance overhead for complex queries."
            },
            {
                "text": "Explain the concept of middleware in web frameworks like FastAPI or Express.",
                "keywords": ["middleware", "request", "response", "interceptor", "logging", "cors", "authentication"],
                "key_feedback": "Define middleware as software functions intercepting HTTP requests and responses for auth, CORS, or logging."
            },
            {
                "text": "What is hashing, and why should user passwords always be hashed before storing them?",
                "keywords": ["hash", "bcrypt", "password", "security", "one-way", "salt", "encryption"],
                "key_feedback": "Explain hashing as a one-way mathematical function making passwords unrecoverable, secured further with salts."
            }
        ],
        "intermediate": [
            {
                "text": "What is database indexing? How does it improve query speed, and what are the trade-offs?",
                "keywords": ["index", "b-tree", "query performance", "write overhead", "search", "storage"],
                "key_feedback": "Discuss indexing speeding up read queries (using B-Trees), at the expense of slower writes and additional disk space."
            },
            {
                "text": "Explain database normalization (1NF, 2NF, 3NF) and when you might choose to denormalize.",
                "keywords": ["normalization", "redundancy", "anomaly", "1nf", "2nf", "3nf", "denormalization", "joins"],
                "key_feedback": "Explain normal forms reducing data redundancy and anomalies, and denormalization combining tables to avoid expensive joins."
            },
            {
                "text": "What is JWT (JSON Web Token)? How is it structured, and how is it used for stateless authentication?",
                "keywords": ["jwt", "stateless", "header", "payload", "signature", "token", "base64"],
                "key_feedback": "Detail the three JWT parts (Header, Payload, Signature) enabling secure, server-side stateless session verification."
            },
            {
                "text": "Explain the difference between SQL injection and Cross-Site Scripting (XSS), and how to prevent them.",
                "keywords": ["sql injection", "xss", "cross-site scripting", "sanitize", "prepared statements", "parameterized"],
                "key_feedback": "Explain SQLi attacking the database (prevented with parameterized queries) and XSS attacking user browsers (prevented by escaping outputs)."
            },
            {
                "text": "What is the difference between synchronous and asynchronous database drivers in backend services?",
                "keywords": ["synchronous", "asynchronous", "blocking", "non-blocking", "event loop", "io-bound"],
                "key_feedback": "Show how async drivers prevent blocking the server's single thread, boosting throughput on high concurrency I/O tasks."
            }
        ],
        "advanced": [
            {
                "text": "Explain ACID properties in database transactions and how different isolation levels affect concurrent queries.",
                "keywords": ["acid", "isolation level", "dirty read", "phantom read", "non-repeatable", "transaction"],
                "key_feedback": "Define Atomicity, Consistency, Isolation, and Durability, and discuss isolation levels (Read Committed, Serializable)."
            },
            {
                "text": "What is vertical vs horizontal scaling? Explain sharding, replication, and load balancing.",
                "keywords": ["sharding", "replication", "horizontal", "vertical", "load balancer", "scale"],
                "key_feedback": "Contrast upgrading single server hardware (vertical) with adding more servers (horizontal), using replication and DB sharding."
            },
            {
                "text": "How do you implement rate limiting in a distributed backend architecture?",
                "keywords": ["rate limiting", "redis", "token bucket", "sliding window", "distributed", "middleware"],
                "key_feedback": "Suggest storing request counts in a distributed cache like Redis and applying algorithms like Token Bucket or Sliding Window."
            },
            {
                "text": "Explain event-driven architecture and how message brokers like RabbitMQ or Kafka handle distributed messages.",
                "keywords": ["event-driven", "message broker", "kafka", "rabbitmq", "pub-sub", "queue", "asynchronous"],
                "key_feedback": "Analyze asynchronous publish-subscribe mechanisms decoupled via message brokers for high scalability and fault tolerance."
            },
            {
                "text": "What is a connection pool in database management, and how do you size it optimally for high traffic?",
                "keywords": ["connection pool", "sizing", "overhead", "threads", "max connections", "limit"],
                "key_feedback": "Explain pooling pre-warmed connections to avoid socket overhead, sizing based on CPU cores, disk I/O, and thread availability."
            }
        ]
    },
    "cloud computing": {
        "beginner": [
            {
                "text": "What is Cloud Computing, and what are the differences between IaaS, PaaS, and SaaS?",
                "keywords": ["iaas", "paas", "saas", "infrastructure", "platform", "software", "cloud"],
                "key_feedback": "Explain IaaS (renting VMs/networking), PaaS (managed app platforms), and SaaS (ready-made web software)."
            },
            {
                "text": "What are public, private, and hybrid cloud deployment models?",
                "keywords": ["public", "private", "hybrid", "shared", "dedicated", "on-premise"],
                "key_feedback": "Define public (shared infrastructure), private (dedicated single-tenant), and hybrid (combining cloud and local servers)."
            },
            {
                "text": "Explain the concept of 'Virtualization' in cloud computing.",
                "keywords": ["virtualization", "hypervisor", "virtual machine", "hardware", "host"],
                "key_feedback": "Explain how a hypervisor abstracts physical hardware to run multiple virtual machines on a single physical host."
            },
            {
                "text": "What is the AWS Free Tier, and what is cloud billing/pay-as-you-go pricing?",
                "keywords": ["free tier", "billing", "pay-as-you-go", "pricing", "cost"],
                "key_feedback": "Explain pay-as-you-go billing charging only for active runtime resources, and free tiers facilitating learning."
            },
            {
                "text": "What are regions and availability zones in cloud infrastructure?",
                "keywords": ["region", "availability zone", "data center", "latency", "redundancy"],
                "key_feedback": "Detail geographic Regions containing multiple isolated Availability Zones (data centers) connected via low latency fiber."
            }
        ],
        "intermediate": [
            {
                "text": "What is Serverless Computing, and what are its main advantages and limitations?",
                "keywords": ["serverless", "lambda", "scale", "cold start", "stateless", "cost-efficiency"],
                "key_feedback": "Describe serverless executing functions on-demand without managing infrastructure, but mention cold start delays."
            },
            {
                "text": "Explain the Shared Responsibility Model in cloud security.",
                "keywords": ["shared responsibility", "security of the cloud", "security in the cloud", "customer", "provider"],
                "key_feedback": "Explain that providers secure physical hosts and networks, while customers secure their applications, OS, and data."
            },
            {
                "text": "What is Infrastructure as Code (IaC), and what tools are commonly used?",
                "keywords": ["iac", "terraform", "cloudformation", "declarative", "version control", "infrastructure"],
                "key_feedback": "Define IaC defining cloud resources in code files (e.g. Terraform) to achieve reproducible infrastructure deployments."
            },
            {
                "text": "Explain the concept of Auto-Scaling and Load Balancing in the cloud.",
                "keywords": ["auto-scaling", "load balancer", "scaling", "traffic", "elasticity", "distribute"],
                "key_feedback": "Describe load balancers distributing requests, and auto-scaling scaling virtual instances up or down based on load."
            },
            {
                "text": "What are containers, and how does Docker differ from a traditional virtual machine?",
                "keywords": ["container", "docker", "virtual machine", "kernel", "hypervisor", "lightweight"],
                "key_feedback": "Contrast VMs virtualizing the full hardware layer with Docker containers sharing the host OS kernel, making them lightweight."
            }
        ],
        "advanced": [
            {
                "text": "Explain Kubernetes architecture. What are pods, deployments, services, and ingress controllers?",
                "keywords": ["kubernetes", "pod", "deployment", "service", "ingress", "control plane", "kubelet"],
                "key_feedback": "Explain the orchestration system components: pods (run containers), services (networking), and ingress (external routing)."
            },
            {
                "text": "How do you design a highly available, multi-region disaster recovery plan in the cloud?",
                "keywords": ["disaster recovery", "rto", "rpo", "active-active", "active-passive", "multi-region", "failover"],
                "key_feedback": "Analyze RTO/RPO limits and DR patterns like Pilot Light, Warm Standby, or multi-region Active-Active routing."
            },
            {
                "text": "Explain Cloud Design Patterns like Circuit Breaker, CQRS, and Event Sourcing.",
                "keywords": ["circuit breaker", "cqrs", "event sourcing", "read-write", "events", "microservices"],
                "key_feedback": "Explain CQRS separating reads from writes, Event Sourcing saving transitions, and Circuit Breaker preventing cascade failures."
            },
            {
                "text": "What is a Service Mesh, and how does it manage service-to-service communication?",
                "keywords": ["service mesh", "istio", "sidecar", "proxy", "mutual tls", "telemetry"],
                "key_feedback": "Analyze how sidecar proxies (like Envoy) manage mTLS, routing rules, and metrics collection transparently."
            },
            {
                "text": "Explain cloud security mechanisms like IAM roles, VPC peering, transit gateways, and security groups.",
                "keywords": ["iam", "vpc peering", "transit gateway", "security group", "network acl", "private link"],
                "key_feedback": "Detail security isolation layers: fine-grained IAM permissions, private VPC networking, and instance-level firewalls."
            }
        ]
    },
    "cyber security": {
        "beginner": [
            {
                "text": "What is phishing, and how can users protect themselves from phishing attacks?",
                "keywords": ["phishing", "email", "spoof", "credentials", "mfa", "link"],
                "key_feedback": "Define phishing as deceptive social engineering emails requesting credentials, mitigated by checking domains and using MFA."
            },
            {
                "text": "Explain the difference between symmetric and asymmetric encryption.",
                "keywords": ["symmetric", "asymmetric", "private key", "public key", "encryption", "speed"],
                "key_feedback": "Compare symmetric (one key for both encrypt/decrypt, fast) with asymmetric encryption (public key encrypts, private key decrypts)."
            },
            {
                "text": "What is a firewall, and how does it protect a network?",
                "keywords": ["firewall", "traffic", "filter", "rules", "port", "packet"],
                "key_feedback": "Explain firewalls monitoring and filtering inbound/outbound network traffic according to predefined security rules."
            },
            {
                "text": "What is multi-factor authentication (MFA), and why is it recommended?",
                "keywords": ["mfa", "factors", "security", "authenticator", "otp", "leak"],
                "key_feedback": "Define MFA requiring multiple validation factors (something you know, have, or are) to prevent credential theft attacks."
            },
            {
                "text": "What is malware, and how does antivirus software detect it?",
                "keywords": ["malware", "virus", "antivirus", "signatures", "heuristic", "detect"],
                "key_feedback": "Discuss malicious software types, and detection techniques like database signatures or behavioral heuristics."
            }
        ],
        "intermediate": [
            {
                "text": "What is the OWASP Top 10, and why is it important for web application security?",
                "keywords": ["owasp", "vulnerabilities", "risks", "web security", "standard"],
                "key_feedback": "Explain OWASP Top 10 as a standardized awareness document outlining the most critical web application security vulnerabilities."
            },
            {
                "text": "Explain how a Man-in-the-Middle (MitM) attack works and how HTTPS protects against it.",
                "keywords": ["mitm", "man-in-the-middle", "eavesdrop", "https", "ssl", "tls", "certificate"],
                "key_feedback": "Discuss attackers intercepting unsecured sessions, and how HTTPS encrypts traffic and validates server certificate identities."
            },
            {
                "text": "What is the difference between vulnerability scanning and penetration testing?",
                "keywords": ["vulnerability scan", "penetration test", "automated", "manual", "exploit", "human"],
                "key_feedback": "Contrast automated, high-level vulnerability scans with manual, creative penetration tests simulating actual hacker exploits."
            },
            {
                "text": "Explain DNS spoofing and ARP poisoning attacks.",
                "keywords": ["dns spoofing", "arp poisoning", "ip", "mac address", "redirect", "cache"],
                "key_feedback": "ARP poisoning maps IP to attacker MAC addresses locally; DNS spoofing alters domain name server resolutions to redirect web traffic."
            },
            {
                "text": "What is Principle of Least Privilege (PoLP), and how is it implemented in enterprise access control?",
                "keywords": ["least privilege", "polp", "access control", "permissions", "role-based"],
                "key_feedback": "Detail limiting user/system access permissions to only the bare minimum required to perform their specific duties."
            }
        ],
        "advanced": [
            {
                "text": "Explain how buffer overflow vulnerabilities occur in C/C++ and how modern OS mitigate them.",
                "keywords": ["buffer overflow", "stack", "aslr", "dep", "canary", "execution"],
                "key_feedback": "Explain writing data past bounds to overwrite memory pointers, mitigated by ASLR (randomizes addresses) and stack canaries."
            },
            {
                "text": "What is Zero Trust Architecture, and what are its core tenets?",
                "keywords": ["zero trust", "never trust", "always verify", "microsegmentation", "least privilege", "identity"],
                "key_feedback": "Analyze 'Never Trust, Always Verify', requiring continuous authorization of every device, user, and session."
            },
            {
                "text": "Explain how Kerberos authentication works in Windows Active Directory environments.",
                "keywords": ["kerberos", "ticket", "kdc", "as", "tgs", "tgt", "active directory"],
                "key_feedback": "Detail the client requesting a ticket-granting-ticket (TGT) from the KDC, used later to request service tickets."
            },
            {
                "text": "What is cryptography's Diffie-Hellman Key Exchange, and how does it achieve perfect forward secrecy?",
                "keywords": ["diffie-hellman", "key exchange", "forward secrecy", "session key", "asymmetric"],
                "key_feedback": "Show how parties derive a shared secret over an insecure channel, ensuring past sessions remain secure even if private keys leak."
            },
            {
                "text": "Explain how SQL injection can lead to Remote Code Execution (RCE) and how to conduct forensic analysis after a breach.",
                "keywords": ["sql injection", "rce", "forensics", "logs", "xp_cmdshell", "command execution"],
                "key_feedback": "Detail functions like xp_cmdshell executing system shell scripts via database engines, and tracing logs for remediation."
            }
        ]
    },
    "data analytics": {
        "beginner": [
            {
                "text": "What is Data Analytics, and what is the difference between structured and unstructured data?",
                "keywords": ["structured", "unstructured", "data", "database", "format", "relational"],
                "key_feedback": "Differentiate structured data (rigid schemas, SQL tables) from unstructured data (photos, free text, audio)."
            },
            {
                "text": "Explain the difference between qualitative and quantitative data.",
                "keywords": ["qualitative", "quantitative", "numerical", "categorical", "descriptive", "measure"],
                "key_feedback": "Contrast quantitative data (numerical values, measurements) with qualitative data (categorical attributes, descriptions)."
            },
            {
                "text": "What are the common stages in a data analysis lifecycle?",
                "keywords": ["stages", "collect", "clean", "analyze", "visualize", "interpret"],
                "key_feedback": "List the common stages: defining goals, collecting data, cleaning, exploring, modeling, and communicating insights."
            },
            {
                "text": "What is data cleaning, and why is it the most time-consuming part of analysis?",
                "keywords": ["cleaning", "missing", "duplicate", "format", "outliers", "quality"],
                "key_feedback": "Discuss removing duplicates, handling missing entries, formatting variables, and standardizing values to ensure data quality."
            },
            {
                "text": "What is the difference between a bar chart, line chart, and scatter plot?",
                "keywords": ["bar", "line", "scatter", "category", "time series", "correlation", "variables"],
                "key_feedback": "Use bar charts for category comparisons, line charts for changes over time, and scatter plots for relationships between two metrics."
            }
        ],
        "intermediate": [
            {
                "text": "What is ETL (Extract, Transform, Load), and how does it differ from ELT?",
                "keywords": ["etl", "elt", "transform", "load", "staging", "data warehouse", "data lake"],
                "key_feedback": "Contrast ETL (transforming data on staging server before loading) with ELT (loading raw data and transforming inside the target lake)."
            },
            {
                "text": "Explain the difference between descriptive, diagnostic, predictive, and prescriptive analytics.",
                "keywords": ["descriptive", "diagnostic", "predictive", "prescriptive", "what happened", "action"],
                "key_feedback": "Differentiate descriptive (what happened), diagnostic (why), predictive (what will happen), and prescriptive (what action to take)."
            },
            {
                "text": "What is a data warehouse, and how does it differ from a relational database and a data lake?",
                "keywords": ["warehouse", "lake", "database", "olap", "oltp", "unstructured", "historical"],
                "key_feedback": "Contrast databases (transactional, OLTP) with data warehouses (historical analytics, OLAP) and data lakes (raw, unstructured files)."
            },
            {
                "text": "Explain what correlation is, and why correlation does not imply causation.",
                "keywords": ["correlation", "causation", "relationship", "cause", "spurious", "variable"],
                "key_feedback": "Define correlation as linear statistical relation, and explain how a third variable or coincidence can cause spurious relationships."
            },
            {
                "text": "What are window functions in SQL, and how do they differ from GROUP BY queries?",
                "keywords": ["window function", "over", "group by", "aggregation", "partition", "rows"],
                "key_feedback": "Show how window functions (`OVER()`) compute aggregations across sets while retaining details of individual rows, unlike GROUP BY."
            }
        ],
        "advanced": [
            {
                "text": "Explain A/B testing statistical methodology, including null hypothesis testing, p-values, and statistical power.",
                "keywords": ["ab testing", "null hypothesis", "p-value", "statistical power", "significance", "type i error"],
                "key_feedback": "Explain designing control and test groups, setting significance levels (alpha/p-value), and calculating power to prevent Type II errors."
            },
            {
                "text": "What is dimensional modeling? Explain star schema vs snowflake schema in data warehousing.",
                "keywords": ["star", "snowflake", "dimension", "fact table", "normalization"],
                "key_feedback": "Contrast star schema (de-normalized dimensions, fast queries) with snowflake schema (normalized dimensions, saves space)."
            },
            {
                "text": "How do you handle missing data (imputation, deletion, modeling) in a large data pipeline?",
                "keywords": ["missing data", "imputation", "mean", "median", "knn", "deletion", "bias"],
                "key_feedback": "Evaluate trade-offs of listwise deletion, simple statistical imputation (mean/median), or advanced model-based imputations (KNN)."
            },
            {
                "text": "Explain the difference between OLAP (Online Analytical Processing) and OLTP (Online Transaction Processing).",
                "keywords": ["olap", "oltp", "analytical", "transactional", "normalization", "queries"],
                "key_feedback": "Differentiate fast, small writes (OLTP) from complex, aggregated read queries over historical data warehouse systems (OLAP)."
            },
            {
                "text": "What is cohort analysis, and how do you calculate user retention rates over time?",
                "keywords": ["cohort", "retention", "customer lifecycle", "churn", "behavior"],
                "key_feedback": "Define cohort analysis tracking groups sharing characteristics over time, analyzing retention tables to find drop-offs."
            }
        ]
    },
    "data science": {
        "beginner": [
            {
                "text": "What is the difference between supervised and unsupervised learning?",
                "keywords": ["supervised", "unsupervised", "label", "target", "features", "classification", "clustering"],
                "key_feedback": "Differentiate supervised learning (trained on labeled data) from unsupervised learning (finding patterns in unlabeled data)."
            },
            {
                "text": "What is overfitting in machine learning, and how do you identify it?",
                "keywords": ["overfitting", "validation", "training error", "generalization", "noise"],
                "key_feedback": "Explain models learning training noise too well, characterized by low training error but high validation/testing error."
            },
            {
                "text": "What is the difference between regression and classification tasks?",
                "keywords": ["regression", "classification", "continuous", "discrete", "categorical", "predict"],
                "key_feedback": "Identify regression predicting continuous numerical values, while classification predicts discrete categorical classes."
            },
            {
                "text": "Explain the purpose of training, validation, and test datasets.",
                "keywords": ["training", "validation", "test", "hyperparameter", "generalization", "tune"],
                "key_feedback": "Explain training models on training set, tuning hyperparameters on validation set, and performing final evaluation on test set."
            },
            {
                "text": "What is a confusion matrix, and what are precision and recall?",
                "keywords": ["confusion matrix", "precision", "recall", "true positive", "false positive", "accuracy"],
                "key_feedback": "Define precision (true positives / predicted positives) and recall (true positives / actual positives) using a confusion grid."
            }
        ],
        "intermediate": [
            {
                "text": "Explain the bias-variance trade-off in machine learning models.",
                "keywords": ["bias", "variance", "trade-off", "underfitting", "overfitting", "error"],
                "key_feedback": "Discuss bias (simple model assumptions, underfitting) vs variance (high model sensitivity, overfitting) and finding the optimal complexity."
            },
            {
                "text": "How do decision trees work, and what is the difference between a decision tree and a random forest?",
                "keywords": ["decision tree", "random forest", "ensemble", "bagging", "bootstrap", "overfitting"],
                "key_feedback": "Describe trees splitting nodes on features, and Random Forest bagging multiple trees to reduce variance and overfitting."
            },
            {
                "text": "What is feature engineering, and how do techniques like one-hot encoding and standardization work?",
                "keywords": ["feature engineering", "one-hot", "standardization", "categorical", "mean", "scaling"],
                "key_feedback": "Explain creating/scaling features: one-hot encoding converts categories to binary cols, standardization shifts mean to 0 and variance to 1."
            },
            {
                "text": "Explain PCA (Principal Component Analysis) and when you would use dimensionality reduction.",
                "keywords": ["pca", "variance", "dimensionality", "eigenvector", "projection", "orthogonal"],
                "key_feedback": "Define PCA projecting data onto orthogonal axes of maximum variance to compress high-dimensional features."
            },
            {
                "text": "What is the difference between L1 (Lasso) and L2 (Ridge) regularization?",
                "keywords": ["l1", "l2", "lasso", "ridge", "sparsity", "penalty", "coefficients"],
                "key_feedback": "Contrast L1 regularization (adds absolute weights penalty, creates sparse weights/feature selection) with L2 (adds squared weights)."
            }
        ],
        "advanced": [
            {
                "text": "Explain the mathematical foundations of Gradient Descent and backpropagation in deep neural networks.",
                "keywords": ["gradient descent", "backpropagation", "derivative", "chain rule", "loss function", "weights"],
                "key_feedback": "Describe using the calculus chain rule to compute gradients of the loss function, propagating errors back to update weights."
            },
            {
                "text": "How do Transformer architectures work, particularly the self-attention mechanism?",
                "keywords": ["transformer", "attention", "query", "key", "value", "parallel", "multi-head"],
                "key_feedback": "Analyze calculating similarity scores between Query, Key, and Value matrices, allowing tokens to weigh other words dynamically."
            },
            {
                "text": "Explain the difference between generative and discriminative models, giving examples of GANs vs classifiers.",
                "keywords": ["generative", "discriminative", "probability", "boundary", "gan", "joint distribution"],
                "key_feedback": "Contrast discriminative models learning boundaries ($P(Y|X)$) with generative models modeling the underlying data distribution ($P(X,Y)$)."
            },
            {
                "text": "What is cross-validation? Compare K-Fold, Stratified K-Fold, and Time Series Split cross-validation.",
                "keywords": ["cross-validation", "k-fold", "stratified", "time series", "leakage", "variance"],
                "key_feedback": "Analyze K-Fold splitting data evenly, Stratified retaining class ratios, and Time Series splits respecting chronology to avoid leakage."
            },
            {
                "text": "How do you handle highly imbalanced datasets (e.g. fraud detection) using advanced techniques?",
                "keywords": ["imbalanced", "smote", "class weights", "focal loss", "resampling", "auc-roc"],
                "key_feedback": "Evaluate oversampling (SMOTE), undersampling, adjusting loss functions (class weights/focal loss), and tracking precision-recall curves."
            }
        ]
    }
}


def normalize_topic(topic: str) -> str:
    """Normalize user/context topic strings to match the OFFLINE_QUESTIONS keys."""
    t = topic.lower().strip()
    if "python" in t:
        return "python"
    elif "java" in t:
        return "java"
    elif "aptitude" in t:
        return "aptitude"
    elif "web" in t:
        return "web development"
    elif "frontend" in t:
        return "frontend developer"
    elif "backend" in t:
        return "backend developer"
    elif "cloud" in t:
        return "cloud computing"
    elif "cyber" in t:
        return "cyber security"
    elif "analytic" in t:
        return "data analytics"
    elif "science" in t:
        return "data science"
    return "python"  # Default fallback


def get_next_question(context: dict, previous_answer: str = None) -> str:
    """
    Ask the next interview question. Attempts Ollama first,
    then falls back to the curated offline questions database.
    """
    topic_normalized = normalize_topic(context.get("topic", "python"))
    difficulty = context.get("difficulty", "beginner").lower()
    if difficulty not in ["beginner", "intermediate", "advanced"]:
        difficulty = "beginner"
    
    q_index = context.get("question_number", 1) - 1  # 0-indexed

    # 1. Attempt Ollama first
    prompt = f"""
You are a friendly AI Interviewer like Mentiza.

Skill: {context.get('topic')}
Difficulty: {context.get('difficulty')}
Question Number: {context.get('question_number')}
Previous Answer: {previous_answer if previous_answer else "None"}

Rules:
- Talk friendly like a mentor.
- If previous answer is wrong or incomplete:
  - Say politely that improvement is needed.
  - Tell what is missing.
  - Ask the user to repeat in proper format.
- If answer is good:
  - Praise shortly.
  - Ask next technical question.
- Ask only ONE question.
- Keep tone supportive and motivating.

Now respond:
"""
    response = call_ollama(prompt)
    if response:
        return response

    # 2. Fallback to offline questions
    questions_list = OFFLINE_QUESTIONS[topic_normalized][difficulty]
    # Wrap index in case question number exceeds 5
    selected_question = questions_list[q_index % len(questions_list)]
    return selected_question["text"]


def evaluate_answer(question: str, answer: str, context: str = "") -> str:
    """
    Evaluate student answer. Attempts Ollama first,
    then falls back to a smart, rule-based offline scoring system.
    """
    # 1. Attempt Ollama first
    prompt = f"""
You are an AI interview evaluator.
Context/Skill: {context}

Question:
{question}

Student Answer:
{answer}

Evaluate on this rubric (0-25 each):
1) Concept accuracy
2) Clarity/communication
3) Technical depth
4) Practical examples

Return strictly:
Score: <0-100>
Breakdown:
- Concept accuracy: <0-25>
- Clarity: <0-25>
- Depth: <0-25>
- Examples: <0-25>
Feedback:
<2-4 actionable bullets to improve>
"""
    response = call_ollama(prompt)
    if response:
        return response

    # 2. Fallback to local rule-based mock evaluation
    topic_normalized = normalize_topic(context)
    difficulty = "beginner" # generic default for looking up details
    
    # Let's find if we can identify which question this was to extract keywords
    keywords = ["concept", "understand", "theory"]
    key_feedback = "Elaborate more on the technical specifications and structural requirements of this topic."
    
    for diff in ["beginner", "intermediate", "advanced"]:
        for q in OFFLINE_QUESTIONS[topic_normalized][diff]:
            # Simple soft match for question
            if question.strip().lower()[:30] in q["text"].lower() or q["text"].lower()[:30] in question.strip().lower():
                keywords = q["keywords"]
                key_feedback = q["key_feedback"]
                break

    answer_clean = answer.strip()
    if len(answer_clean) < 15:
        # Penalize extremely short answers
        return f"""Score: 40
Breakdown:
- Concept accuracy: 10
- Clarity: 10
- Depth: 10
- Examples: 10
Feedback:
- Your response is too brief. Please provide a more detailed and technical response.
- Use industry-specific terms and explain the conceptual mechanics in your own words.
"""

    # Calculate matches
    matched = [kw for kw in keywords if kw in answer_clean.lower()]
    missed = [kw for kw in keywords if kw not in answer_clean.lower()]
    
    match_ratio = len(matched) / len(keywords) if keywords else 1.0
    
    # Calculate rubric categories (out of 25)
    accuracy = int(12 + (match_ratio * 13))
    clarity = int(15 + min(5, len(answer_clean) // 50))
    depth = int(10 + (match_ratio * 15))
    
    # check if user gave an example keyword
    has_example = "example" in answer_clean.lower() or "instance" in answer_clean.lower() or "like" in answer_clean.lower()
    examples = int(12 + (6 if has_example else 0) + (match_ratio * 7))

    # Cap at 25
    accuracy = min(25, accuracy)
    clarity = min(25, clarity)
    depth = min(25, depth)
    examples = min(25, examples)
    
    total_score = accuracy + clarity + depth + examples
    
    feedback_bullets = []
    if matched:
        feedback_bullets.append(f"- Excellent job incorporating key terms like {', '.join(matched[:3])} in your answer.")
    else:
        feedback_bullets.append("- Work on including more technical keywords directly related to the question.")
        
    if missed:
        feedback_bullets.append(f"- To improve, consider explaining: {', '.join(missed[:3])}.")
        
    feedback_bullets.append(f"- {key_feedback}")
    
    feedback_str = "\n".join(feedback_bullets)
    
    return f"""Score: {total_score}
Breakdown:
- Concept accuracy: {accuracy}
- Clarity: {clarity}
- Depth: {depth}
- Examples: {examples}
Feedback:
{feedback_str}
"""


def extract_score_and_feedback(feedback_text: str) -> Tuple[float, str, Dict[str, float]]:
    score = 0.0
    match = re.search(r"Score[:\s]+([0-9]{1,3}(?:\.[0-9]+)?)", feedback_text)
    if match:
        try:
            score = float(match.group(1))
        except ValueError:
            score = 0.0

    breakdown = {
        "concept_accuracy": 0.0,
        "clarity": 0.0,
        "depth": 0.0,
        "examples": 0.0,
    }
    patterns = {
        "concept_accuracy": r"Concept accuracy[:\s]+([0-9]{1,2}(?:\.[0-9]+)?)",
        "clarity": r"Clarity[:\s]+([0-9]{1,2}(?:\.[0-9]+)?)",
        "depth": r"Depth[:\s]+([0-9]{1,2}(?:\.[0-9]+)?)",
        "examples": r"Examples[:\s]+([0-9]{1,2}(?:\.[0-9]+)?)",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, feedback_text, re.IGNORECASE)
        if m:
            try:
                breakdown[key] = float(m.group(1))
            except ValueError:
                pass

    cleaned = "\n".join(line.strip() for line in feedback_text.splitlines() if line.strip())
    return score, cleaned, breakdown


def generate_interview_summary(data: dict) -> str:
    """
    Final Mentiza-style summary. Attempts Ollama first,
    then falls back to generating a personalized summary report.
    """
    # 1. Attempt Ollama first
    prompt = f"""
You are an AI Mentor like Mentiza.

Interview Data:
{json.dumps(data, indent=2)}

Create:
1. Motivation message (2 lines)
2. Strengths
3. Weaknesses
4. Learning roadmap (step-by-step)

Tone: Friendly, hopeful, encouraging.
"""
    response = call_ollama(prompt)
    if response:
        return response

    # 2. Fallback to offline summary report
    qa_pairs = data.get("qa_pairs", [])
    scores = data.get("scores", [])
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    # Identify strong and weak questions
    strengths = []
    weaknesses = []
    
    for pair in qa_pairs:
        score = pair.get("score", 0)
        q_text = pair.get("question", "")
        # truncate
        q_short = q_text[:50] + "..." if len(q_text) > 50 else q_text
        if score >= 75:
            strengths.append(f"- Strong conceptual grasp of: {q_short}")
        else:
            weaknesses.append(f"- Needs additional review of: {q_short}")
            
    if not strengths:
        strengths.append("- Exhibited standard understanding of introductory concepts.")
    if not weaknesses:
        weaknesses.append("- Solid performance across the board; continue deep-diving into advanced design patterns.")

    motivation = (
        "Congratulations on completing your Skillin AI Mentor interview session today! "
        f"You finished with an average score of {avg_score:.1f}%. Keep practicing to build confidence."
    )

    summary_report = f"""Skillin AI Mentor Session Report
--------------------------------------
Motivation:
{motivation}

Strengths Identified:
{chr(10).join(strengths)}

Areas for Improvement:
{chr(10).join(weaknesses)}

Custom Learning Roadmap:
1. Revise the foundational theoretical architecture of topics where you scored lower.
2. Formulate practical code implementations or numerical exercises for those concepts.
3. Schedule a follow-up interview session on Skillin to test your progress!
"""
    return summary_report.strip()


def chat_with_mentor(message: str, history: list = None) -> str:
    """
    General mentor chat mode.
    """
    history_text = ""
    if history:
        for h in history:
            history_text += f"User: {h['user']}\nMentor: {h['mentor']}\n"

    prompt = f"""
You are Skillin AI Mentor.
You are friendly, patient, and technical like Mentiza.

Conversation:
{history_text}

User: {message}
Mentor:
"""
    response = call_ollama(prompt)
    if response:
        return response
        
    return "Hello! I am your offline Skillin AI Mentor. Please make sure Ollama is running locally for full conversational capabilities."
