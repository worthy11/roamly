## Startup instructions

Terminal 1: `uvicorn main:app --reload` <br />
Terminal 2: `npm run dev` <br />
Open app via npm <br />

## Endpoints

For endpoints always use backticks with the API_BASE variable like so:

```js
const response = await fetch(`${API_BASE}/trips/`);
```

Import the variable at the top of the file like so:

```js
import { API_BASE } from "./config";
```

ALWAYS follow the path with a slash, DO NOT do this:

```js
const response = await fetch(`${API_BASE}/trips`);
```

or this:

```js
const response = await fetch(`/${API_BASE}/trips`);
```

or this:

```js
const response = await fetch(`/${API_BASE}/trips/`);
```

NO SLASH at the start, YES SLASH at the end.
