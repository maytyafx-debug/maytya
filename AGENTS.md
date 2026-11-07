# Metatya repository instructions

Before changing any user-facing page, read `docs/design-system/metatya-frontend-standards.md`.

## Frontend rules

- The currently deployed website is a static HTML/CSS/JavaScript site in `docs/`, published with GitHub Pages.
- Preserve the existing stack unless a framework migration is explicitly approved. Do not add React, Next.js, Tailwind, animation libraries, paid services, or external runtime dependencies merely because a reference library uses them.
- Build mobile-first and verify RTL Persian layout, keyboard access, focus states, reduced-motion behavior, responsive breakpoints, and real link/button behavior.
- Keep Metatya's design tokens and visual identity consistent while giving each page a distinct layout appropriate to its purpose.
- Use external skills and component galleries as references, not as unquestioned authorities. Verify license, dependencies, accessibility, performance, and commercial-use terms before copying or integrating code/assets.
- Use Google Android skills only for native Android/Jetpack Compose work; use SwiftUI guidance only for native iOS work. Do not imply the website is already a native mobile app.
- Do not introduce placeholders that look like working features. Clearly label incomplete, experimental, or locally stored features.
- Prefer complete, maintainable files and small native implementations over unnecessary dependencies.

## Safe GitHub workflow

- Before editing an existing file, fetch its latest contents and blob SHA.
- Make the smallest coherent change, then fetch the file again and verify the intended content.
- Do not claim browser testing, visual QA, deployment, or workflow success unless the corresponding check actually ran and succeeded.
- After changes under `docs/`, inspect the GitHub Pages workflow and report its real status.
