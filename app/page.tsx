// app/page.tsx
"use client";
import { useState } from "react";
import { Button } from "@govtechmy/myds-react/button";
import { TextArea } from "@govtechmy/myds-react/textarea";
import { ThemeSwitch } from "@govtechmy/myds-react/theme-switch";
import { ThemeProvider } from "@govtechmy/myds-react/hooks";
import { Spinner } from "@govtechmy/myds-react/spinner";
import {
  Callout,
  CalloutTitle,
  CalloutContent,
} from "@govtechmy/myds-react/callout";
import { Tag } from "@govtechmy/myds-react/tag";
import StackBlitzEditor from "./components/LiveEditor";
import Link from "next/link";

export default function App() {
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
  const [data, setData] = useState({});
  const [completed, setCompleted] = useState(false);
  const [newInput, setNewInput] = useState("");

  const handleRun = async () => {
    setLoading(true);
    try {
      setStatus("Validating");
      const response1 = await fetch(
        `/api/py/validate-new-prompt?prompt=${encodeURIComponent(input)}`,
        {
          // URI encode prompt
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      const data1 = await response1.json();

      if (data1.valid) {
        setStatus("Learning about the prompt");
        const response2 = await fetch(
          `/api/py/task_planning?prompt=${encodeURIComponent(input)}`,
          {
            // URI encode prompt
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        const data2 = await response2.json();

        setStatus("Designing the Layout");
        const wireframeRes = await fetch(`/api/py/wireframe_gen`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data2),
        }).then((res) => res.json());

        setStatus("Gathering knowledge");
        const contextRes = await fetch(`/api/py/assemble_context`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ task: data2, wireframe: wireframeRes }),
        }).then((res) => res.json());

        setStatus("Generating the code");
        const generationRes = await fetch(`/api/py/generate_component`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ task: data2, context: contextRes }),
        }).then((res) => res.json());

        const cleanCode = generationRes.replace(/^```tsx\n?|\n?```$/g, "");
        setCode(cleanCode);
        setData({ task: data2, wireframe: wireframeRes, tsx: cleanCode });
        setStatus("Completed");
        setCompleted(true);
      } else {
        setStatus("Invalid Prompt");
        console.warn("Prompt validation failed:", data1);
      }
    } catch (error) {
      console.error("Error during handleRun:", error);
      setStatus("Error occurred");
    }
    setLoading(false);
  };

  const handleRunIter = async () => {
    setLoading_iter(true);
    try {
      let updatedPrompt: any = { ...data };
      updatedPrompt["update_prompt"] = newInput;

      setStatus("Learning about the update");
      const update_task_response = await fetch(`/api/py/task_planning_iter`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedPrompt),
      });
      if (!update_task_response.ok)
        throw new Error(
          `Task planning iter failed: ${update_task_response.statusText}`
        );
      const updatetaskObject = await update_task_response.json();

      let context_update_body: any;
      let currentWireframe = updatedPrompt.wireframe;

      if (updatetaskObject.update.wireframe) {
        setStatus("Updating the Layout");
        let wireframe_update_body: { [key: string]: any } = {
          task: updatetaskObject,
          wireframe: updatedPrompt.wireframe,
        };

        const updatedWireframeRes = await fetch(`/api/py/wireframe_iter`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(wireframe_update_body),
        });
        if (!updatedWireframeRes.ok)
          throw new Error(
            `Wireframe iter failed: ${updatedWireframeRes.statusText}`
          );
        currentWireframe = await updatedWireframeRes.json();

        context_update_body = {
          task: updatetaskObject,
          wireframe: currentWireframe,
        };
      } else {
        context_update_body = {
          task: updatetaskObject,
          wireframe: updatedPrompt.wireframe,
        };
      }

      setStatus("Gathering knowledge");
      const updatedContextRes = await fetch(`/api/py/assemble_context_iter`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(context_update_body),
      });
      if (!updatedContextRes.ok)
        throw new Error(
          `Assemble context iter failed: ${updatedContextRes.statusText}`
        );
      const updatedContext = await updatedContextRes.json();

      setStatus("Updating code");
      let component_update_body = {
        task: updatetaskObject,
        context: updatedContext,
        tsx: updatedPrompt.tsx,
      };

      const update_component_response = await fetch(
        `/api/py/generate_component_iterate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(component_update_body),
        }
      );
      if (!update_component_response.ok)
        throw new Error(
          `Generate component iter failed: ${update_component_response.statusText}`
        );
      const update_component_result = await update_component_response.json();

      const cleanCode = update_component_result.replace(
        /^```tsx\n?|\n?```$/g,
        ""
      );
      setCode(cleanCode);
      setData({
        task: updatetaskObject,
        wireframe: currentWireframe,
        tsx: cleanCode,
      });
      setStatus("Completed");
      setNewInput("");
    } catch (error) {
      console.error("Error during handleRunIter:", error);
      setStatus("Error during update");
    }
    setLoading_iter(false);
  };

  return (
    <ThemeProvider>
      <main className="bg-bg-white">
        <div className="mx-auto px-4 sm:px-6 lg:px-8 xl:px-10 2xl:px-12">
          <div className="flex flex-wrap items-center pt-4 mt-8 mb-0 mx-4 md:mx-0">
            <div className="flex-col">
              <h1 className="text-txt-black-900 text-3xl mt-auto sm:px-6 xl:px-8 2xl:px-10 font-bold tracking-tight">
                Jen
              </h1>
              <p className="text-txt-black-900 text-sm mt-auto font-bold tracking-tight sm:px-6 xl:px-8 2xl:px-10 hidden sm:block">
                Generative UI using the{" "}
                <Link
                  href="https://design.digital.gov.my/"
                  className="underline"
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
          <div className="p-4 flex flex-col lg:flex-row gap-6 xl:gap-8 2xl:gap-10 min-h-80%">
            <div className="lg:flex-[1] space-y-4 rounded-lg shadow-card p-6 w-full lg:w-auto xl:w-1/3 2xl:w-1/4">
              <Tag size="small" dot={true} variant="danger">
                dev Build
              </Tag>
              <Callout className="p-2" variant="warning" dismissible>
                <CalloutTitle>
                  Notice
                </CalloutTitle>
                <CalloutContent>
                Gemini model is currently downgraded to <code className="bg-bg-white drop-shadow-md">Gemini-2.0-flash</code> for
                speed and reliability<br/>(Generated code may be in lower quality)
                </CalloutContent>
              </Callout>
              <div
                className={`border rounded-md p-6 ${
                  completed
                    ? "bg-bg-white-disabled dark:bg-bg-dark-disabled"
                    : "bg-bg-white dark:bg-bg-dark-alt"
                }`}
              >
                {" "}
                <h2
                  className={`flex ${
                    completed
                      ? "text-txt-black-disabled dark:text-txt-dark-disabled"
                      : "text-txt-black-900 dark:text-txt-dark"
                  } text-xl mb-4 justify-center`}
                >
                  {" "}
                  Describe a component
                </h2>
                <TextArea
                  className="h-50 min-h-[50px] mb-4 w-full"
                  size="small"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Describe your desired component..."
                  disabled={completed}
                />
                <Button
                  className="ml-auto w-full sm:w-auto xl:w-auto 2xl:w-auto"
                  onClick={handleRun}
                  disabled={loading || completed || !input}
                >
                  {loading ? (
                    <>
                      <span>Processing...</span>
                      <Spinner color="white" />
                    </>
                  ) : (
                    "Submit"
                  )}
                </Button>
              </div>

              {loading && (
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
                  <div className="border rounded-md p-6 bg-bg-white dark:bg-bg-dark-alt">
                    <h2 className="flex text-txt-black-900 dark:text-txt-dark text-xl mb-4 justify-center">
                      Describe an update or modification
                    </h2>
                    <TextArea
                      className="h-50 min-h-[50px] mb-4 w-full bg-bg-white dark:bg-bg-dark"
                      size="small"
                      value={newInput}
                      onChange={(e) => setNewInput(e.target.value)}
                      placeholder="Enter an update for the component..."
                    />
                    <Button
                      className="ml-auto w-full sm:w-auto xl:w-auto 2xl:w-auto"
                      onClick={handleRunIter}
                      disabled={loading_iter || !newInput}
                    >
                      {loading_iter ? (
                        <>
                          <span>Processing...</span>
                          <Spinner color="white" />
                        </>
                      ) : (
                        "Submit"
                      )}
                    </Button>
                  </div>

                  {loading_iter && (
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

            <div className="lg:flex-[3] rounded-lg shadow-card w-full xl:w-2/3 2xl:w-3/4 overflow-hidden">
              <StackBlitzEditor code={code} />
            </div>
          </div>
        </div>
      </main>
    </ThemeProvider>
  );
}
