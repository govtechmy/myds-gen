"use client";
import { useState, useRef } from "react";
import { Button } from "@govtechmy/myds-react/button";
import { TextArea } from "@govtechmy/myds-react/textarea";
import { Input } from "@govtechmy/myds-react/input";
import { ThemeSwitch } from "@govtechmy/myds-react/theme-switch";
import { ThemeProvider } from "@govtechmy/myds-react/hooks";
import { Spinner } from "@govtechmy/myds-react/spinner";
import {
  Callout,
  CalloutTitle,
  CalloutContent,
} from "@govtechmy/myds-react/callout";
import { Tag } from "@govtechmy/myds-react/tag";
import {
  Select,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectItem,
} from "@govtechmy/myds-react/select";
import {
  Accordion,
  AccordionTrigger,
  AccordionContent,
  AccordionItem,
} from "@govtechmy/myds-react/accordion";
import { SettingIcon } from "@govtechmy/myds-react/icon";
import StackBlitzEditor from "./components/LiveEditor";
import Link from "next/link";

const API_BASE_URL = "https://jen-api.onrender.com";
const INIT_STREAM_ENDPOINT = `${API_BASE_URL}/init_prompt_stream`;
const ITER_STREAM_ENDPOINT = `${API_BASE_URL}/iteration_stream`;

const cleanCodeMarkers = (codeChunk: string): string => {
  return codeChunk.replace(/^(\/\/)?```tsx\\n?|\\n?(\/\/)?```$/g, "");
};

export default function App() {
  const [gemini_key, setKey] = useState("");
  const [model, setModel] = useState("");
  const [input, setInput] = useState("");
  const [code, setCode] =
    useState(`import { Button } from "@govtechmy/myds-react/button";
import { Callout, CalloutAction, CalloutTitle, CalloutContent } from "@govtechmy/myds-react/callout";
import { Link } from "@govtechmy/myds-react/link";

export default function App() {
  return (
    <Callout>
      <CalloutTitle>Your component will be rendered here</CalloutTitle>
      <CalloutContent>
        Built with the Malaysia Government Design System (MYDS)
      </CalloutContent>
      <CalloutAction>
        
        <Link href="https://design.digital.gov.my" primary underline="None" newTab>
          <Button variant="default-outline">
            {/* The link's destination should be indicated here. */}
            Learn More
          </Button>
        </Link>

      </CalloutAction>
    </Callout>
  );
};`);
  const [loading, setLoading] = useState(false);
  const [loading_iter, setLoading_iter] = useState(false);
  const [status, setStatus] = useState("");
  const [apiFinalState, setApiFinalState] = useState<any>(null);
  const [completed, setCompleted] = useState(false);
  const [newInput, setNewInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const streamBufferRef = useRef("");

  const handleApiError = (err: any, context: string) => {
    console.error(`Error during ${context}:`, err);
    let message = "An unknown error occurred.";
    if (err instanceof Error) {
      message = err.message;
    } else if (typeof err === "string") {
      message = err;
    }
    setError(`Error during ${context}: ${message}`);
    setStatus("Error");
  };

  const processStream = async (
    response: Response,
    onChunk: (codeChunk: string) => void,
    onFinalState: (finalState: any) => void,
    onComplete: () => void,
    onError: (err: any) => void
  ) => {
    if (!response.body) {
      throw new Error("Response body is missing");
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let done = false;
    streamBufferRef.current = "";

    while (!done) {
      try {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;

        if (value) {
          const decodedChunk = decoder.decode(value, { stream: !done });
          streamBufferRef.current += decodedChunk;

          let newlineIndex;
          while ((newlineIndex = streamBufferRef.current.indexOf("\n")) >= 0) {
            const line = streamBufferRef.current.slice(0, newlineIndex).trim();
            streamBufferRef.current = streamBufferRef.current.slice(
              newlineIndex + 1
            );

            if (!line) continue;

            try {
              const parsedArray = JSON.parse(line);

              if (Array.isArray(parsedArray) && parsedArray.length === 2) {
                const type = parsedArray[0];
                const content = parsedArray[1];

                if (type === "chunk") {
                  if (typeof content === "string") {
                    onChunk(cleanCodeMarkers(content));
                  } else {
                    console.warn(
                      "Received chunk with non-string content:",
                      content
                    );
                  }
                } else if (type === "final_state") {
                  let finalStateObject = content;
                  if (typeof content === "string") {
                    try {
                      finalStateObject = JSON.parse(content);
                    } catch (innerParseError) {
                      console.error(
                        "Error parsing final_state content string:",
                        innerParseError,
                        "Content:",
                        content
                      );
                    }
                  }
                  console.log(
                    "Processing final_state object:",
                    finalStateObject
                  );
                  onFinalState(finalStateObject);
                } else {
                  console.warn("Unknown chunk type received:", type);
                }
              } else {
                console.warn(
                  "Parsed line is not a valid 2-element array:",
                  parsedArray
                );
              }
            } catch (parseError) {
              console.error(
                "Error parsing stream line JSON:",
                parseError,
                "Line:",
                line
              );
            }
          }
        }

        if (done) {
          const finalLine = streamBufferRef.current.trim();
          if (finalLine) {
            try {
              const parsedArray = JSON.parse(finalLine);
              if (Array.isArray(parsedArray) && parsedArray.length === 2) {
                const type = parsedArray[0];
                const content = parsedArray[1];
                if (type === "chunk" && typeof content === "string") {
                  onChunk(cleanCodeMarkers(content));
                } else if (type === "final_state") {
                  let finalStateObject = content;
                  if (typeof content === "string") {
                    try {
                      finalStateObject = JSON.parse(content);
                    } catch (innerParseError) {
                      console.error(
                        "Error parsing final_state content string (final chunk):",
                        innerParseError,
                        "Content:",
                        content
                      );
                    }
                  }
                  onFinalState(finalStateObject);
                }
              }
            } catch (parseError) {
              console.error(
                "Error parsing final stream line JSON:",
                parseError,
                "Line:",
                finalLine
              );
            }
          }
          streamBufferRef.current = "";
        }
      } catch (streamError) {
        done = true;
        onError(streamError);
        return;
      }
    }

    onComplete();
  };

  const handleRun = async () => {
    setLoading(true);
    setCompleted(false);
    setCode("");
    setApiFinalState(null);
    setStatus(`${model} is thinking`);
    setError(null);

    try {
      const response = await fetch(`${INIT_STREAM_ENDPOINT}?prompt=${input}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Gemini-API-Key": gemini_key,
          "X-Model-Type": model,
        },
      });

      if (!response.ok) {
        const errorText = await response
          .text()
          .catch(() => `HTTP error! status: ${response.status}`);
        throw new Error(errorText || `HTTP error! status: ${response.status}`);
      }

      await processStream(
        response,
        (chunk) => setCode((prev) => prev + chunk),
        (finalState) => {
          console.log("Received final state:", finalState);
          setApiFinalState(finalState);
        },
        () => {
          setStatus("Completed");
          setCompleted(true);
          console.log("Initial stream completed.");
        },
        (err) => handleApiError(err, "initial stream processing")
      );
    } catch (error) {
      handleApiError(error, "initial generation request");
    } finally {
      setLoading(false);
      if (status !== "Completed" && status !== "Error") {
        setStatus("");
      }
    }
  };

  const handleRunIter = async () => {
    if (!apiFinalState) {
      setError(
        "Cannot iterate without initial generation data (final_state missing). Please run the initial prompt first."
      );
      setStatus("Error");
      return;
    }

    setLoading_iter(true);
    setStatus(`${model} is thinking`);
    setError(null);
    let isFirstChunk = true;

    try {
      const response = await fetch(ITER_STREAM_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Gemini-API-Key": gemini_key,
          "X-Model-Type": model,
        },
        body: JSON.stringify({
          previous_state: apiFinalState,
          update_prompt: newInput,
        }),
      });

      if (!response.ok) {
        const errorText = await response
          .text()
          .catch(() => `HTTP error! status: ${response.status}`);
        throw new Error(errorText || `HTTP error! status: ${response.status}`);
      }

      await processStream(
        response,
        (chunk) => {
          if (isFirstChunk) {
            setCode(chunk);
            isFirstChunk = false;
          } else {
            setCode((prev) => prev + chunk);
          }
        },
        (finalState) => {
          console.log("Received updated final state:", finalState);
          setApiFinalState(finalState);
        },
        () => {
          setStatus("Completed");
          setNewInput("");
          console.log("Iteration stream completed.");
        },
        (err) => handleApiError(err, "iteration stream processing")
      );
    } catch (error) {
      handleApiError(error, "iteration request");
    } finally {
      setLoading_iter(false);
      if (status !== "Completed" && status !== "Error") {
        setStatus("");
      }
    }
  };

  return (
    <ThemeProvider>
      <main className="bg-bg-white">
        <div className="mx-auto px-4 sm:px-6 lg:px-8 xl:px-10 2xl:px-12">
          <div className="flex flex-wrap items-center pt-4 mt-8 mb-0 mx-4 md:mx-0">
            <div className="flex-col">
              <h1 className="text-txt-black-900 text-3xl mt-auto sm:px-6 xl:px-8 2xl:px-10 font-bold tracking-tight">
                MYDS - Gen
              </h1>
              <p className="text-txt-black-900 text-sm mt-auto font-bold tracking-tight sm:px-6 xl:px-8 2xl:px-10 hidden sm:block">
                Generative UI using the{" "}
                <Link
                  href="https://design.digital.gov.my/"
                  className="underline"
                  target="_blank"
                >
                  MYDS
                </Link>{" "}
                library
              </p>
            </div>
            <div className="ml-auto mt-auto sm:px-6 xl:px-8 2xl:px-10">
              <ThemeSwitch as="select" />
            </div>
          </div>
          <div className="p-4 flex flex-col lg:flex-row gap-6 xl:gap-8 2xl:gap-10">
            <div className="lg:flex-[1] space-y-4 rounded-lg shadow-card bg-bg-white dark:bg-bg-dark-alt p-6 w-full lg:w-auto xl:w-1/3 2xl:w-1/4">
              <Tag size="small" dot={true} variant="danger">
                dev Build
              </Tag>

              <Accordion
                type="single"
                defaultValue="settings"
                collapsible={true}
              >
                <AccordionItem key="settings" value="settings">
                  <AccordionTrigger className="">
                    <div className="flex justify-start gap-2 items-center text-txt-black-500">
                      <SettingIcon /> Settings
                    </div>
                  </AccordionTrigger>
                  <AccordionContent asChild>
                    <div>
                      <Callout className="" variant="info" dismissible>
                        <CalloutTitle>Notice</CalloutTitle>
                        <CalloutContent>
                          Get your free Gemini API Key from{" "}
                          <Link
                            href="https://aistudio.google.com/apikey"
                            className="underline text-txt-primary"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            Google AI Studio
                          </Link>{" "}
                          !
                        </CalloutContent>
                      </Callout>
                      <div className="py-4">
                        <h2 className="text-txt-black-900">
                          Gemini API Key{" "}
                          <span className="text-danger-500 italic text-xs align-top">
                            *required
                          </span>
                        </h2>
                        <Input
                          type="password"
                          required
                          placeholder="Your Gemini API key eg: AIxxxx.... "
                          onChange={(e) => setKey(e.target.value)}
                        />
                      </div>
                      <div className="py-4">
                        <h2 className="text-txt-black-900">
                          Gemini Model Selection{" "}
                          <span className="text-danger-500 italic text-xs align-top">
                            *required
                          </span>
                        </h2>
                        <Select
                          size="small"
                          variant="outline"
                          onValueChange={(e) => setModel(e)}
                        >
                          <SelectTrigger className="max-h-34">
                            <SelectValue label="model" placeholder="Select" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Gemini-2.0-flash">
                              Gemini-2.0-flash (fast, medium quality)
                            </SelectItem>
                            <SelectItem value="Gemini-2.5-flash">
                              Gemini-2.5-flash (slow, great quality)
                            </SelectItem>
                            <SelectItem value="Gemini-2.5-pro">
                              Gemini-2.5-pro (slower, high quality)
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>

              {error && (
                <Callout
                  variant="danger"
                  dismissible
                  onDismiss={() => setError(null)}
                  className="max-h-100 truncate"
                >
                  <CalloutTitle>Error</CalloutTitle>
                  <CalloutContent>{error}</CalloutContent>
                </Callout>
              )}

              <div
                className={`border rounded-md p-6 ${
                  loading || loading_iter
                    ? "bg-bg-white-disabled dark:bg-bg-dark-disabled"
                    : "bg-bg-white dark:bg-bg-dark-alt"
                }`}
              >
                <h2
                  className={`flex ${
                    loading || loading_iter
                      ? "text-txt-black-disabled dark:text-txt-dark-disabled"
                      : "text-txt-black-900 dark:text-txt-dark"
                  } text-xl mb-4 justify-center`}
                >
                  Describe a component
                </h2>
                <TextArea
                  className="h-50 min-h-[50px] mb-4 w-full"
                  size="small"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Describe your desired component (eg: a pricing component)..."
                  disabled={loading || loading_iter}
                />
                <Button
                  className="ml-auto w-full sm:w-auto xl:w-auto 2xl:w-auto"
                  onClick={handleRun}
                  disabled={
                    loading || loading_iter || !input || !gemini_key || !model
                  }
                >
                  {loading ? (
                    <>
                      <span>Generating...</span>
                      <Spinner color="white" />
                    </>
                  ) : (
                    "Submit"
                  )}
                </Button>
              </div>

              {loading && status !== "Completed" && status !== "Error" && (
                <Callout className="p-2" variant="info">
                  <CalloutTitle>
                    {status}
                    <span className="inline-block animate-bounce ml-1">.</span>
                    <span className="inline-block animate-bounce [animation-delay:150ms]">
                      .
                    </span>
                    <span className="inline-block animate-bounce [animation-delay:300ms]">
                      .
                    </span>
                  </CalloutTitle>
                </Callout>
              )}

              {completed && (
                <>
                  <div className="w-[1px] bg-bg-black-400 h-10 mx-auto"></div>
                  <div
                    className={`border rounded-md p-6 ${
                      loading || loading_iter
                        ? "bg-bg-white-disabled"
                        : "bg-bg-white"
                    }`}
                  >
                    <h2
                      className={`flex ${
                        loading || loading_iter
                          ? "text-txt-black-disabled"
                          : "text-txt-black-900"
                      } text-xl mb-4 justify-center`}
                    >
                      Describe an update or modification
                    </h2>
                    <TextArea
                      className="h-50 min-h-[50px] mb-4 w-full bg-bg-white dark:bg-bg-dark"
                      size="small"
                      value={newInput}
                      onChange={(e) => setNewInput(e.target.value)}
                      placeholder="Enter an update for the component (eg: add a sign up button)..."
                      disabled={loading || loading_iter || !apiFinalState} // Disable if loading or no final state
                    />
                    <Button
                      className="ml-auto w-full sm:w-auto xl:w-auto 2xl:w-auto"
                      onClick={handleRunIter}
                      disabled={
                        loading || loading_iter || !newInput || !apiFinalState
                      }
                    >
                      {loading_iter ? (
                        <>
                          <span>Updating...</span>
                          <Spinner color="white" />
                        </>
                      ) : (
                        "Update"
                      )}
                    </Button>
                    {!apiFinalState && !loading && !loading_iter && (
                      <p className="text-xs text-danger-500 mt-2">
                        Initial generation must complete successfully before
                        iterating.
                      </p>
                    )}
                  </div>

                  {loading_iter &&
                    status !== "Completed" &&
                    status !== "Error" && (
                      <Callout className="p-2" variant="info">
                        <CalloutTitle>
                          {status}
                          <span className="inline-block animate-bounce ml-1">
                            .
                          </span>
                          <span className="inline-block animate-bounce [animation-delay:150ms]">
                            .
                          </span>
                          <span className="inline-block animate-bounce [animation-delay:300ms]">
                            .
                          </span>
                        </CalloutTitle>
                      </Callout>
                    )}
                </>
              )}
            </div>

            <div className="lg:flex-[3] rounded-lg shadow-card w-full xl:w-2/3 2xl:w-3/4 min-h-[50vh] h-[50vh] md:h-[90vh]">
              <StackBlitzEditor code={code} />
            </div>
          </div>
        </div>
      </main>
    </ThemeProvider>
  );
}
