import { useState } from "react"
import { withAuthenticator } from "@aws-amplify/ui-react"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { JsonInputEditor } from "@/components/json-input-editor"
import { JsonOutputEditor } from "@/components/json-output-editor"
import { CurriculumRenderer } from "@/components/curriculum-renderer"
import { createOutputJsonApi } from "@/pages/api/getOutputjson"
import { flushSync } from "react-dom"


function CreateCurriculum() {
  const [inputJson, setInputJson] = useState("")
  const [outputJson, setOutputJson] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [activeTab, setActiveTab] = useState("input")
  const [isInputValid, setIsInputValid] = useState(false)
  const [outputError, setOutputError] = useState(false)

  const handleProcessJson = async () => {
    setIsProcessing(true)
    try {
      const responseData = await createOutputJsonApi.getOutputJson({ inputJson: inputJson })
      if (!responseData) {
        setOutputError(true)
        return
      }
      flushSync(() => {
        setOutputJson(JSON.stringify(responseData, null, 2))
      })
      setActiveTab("output")
    } catch (error) {
      console.error("Error processing JSON:", error)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-full mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          </Link>
        </div>

        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Create New Curriculum</h1>
          <p className="text-muted-foreground">Build JSON-based curriculum structures with rich content support</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-blue-500">
            <TabsTrigger value="input" className="text-white cursor-pointer">Input JSON</TabsTrigger>
            <TabsTrigger value="output" className="text-white cursor-pointer">Output JSON</TabsTrigger>
            <TabsTrigger value="preview" className="text-white cursor-pointer">Curriculum Preview</TabsTrigger>
          </TabsList>

          <TabsContent value="input" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Course Structure Input</CardTitle>
                <CardDescription>
                  Define your course structure with sections and file IDs.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <JsonInputEditor value={inputJson} onChange={setInputJson} onValidationChange={setIsInputValid} />
                <div className="flex justify-end mt-4">
                  <Button
                    onClick={handleProcessJson}
                    disabled={!inputJson.trim() || !isInputValid || isProcessing}
                    className="min-w-32 cursor-pointer bg-blue-500 text-white hover:bg-blue-600"
                  >
                    {isProcessing ? "Processing..." : "Generate Curriculum"}
                  </Button>
                </div>
                {inputJson.trim() && !isInputValid && (
                  <div className="mt-2 text-sm text-muted-foreground">
                    Please fix the JSON validation errors above before generating the curriculum.
                  </div>
                )}
                {outputError && (
                  setTimeout(() => {
                    setOutputError(false);
                  }, 5000),
                  <div className="mt-2 text-sm text-destructive">
                    Failed to process JSON. Please try again.
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="output" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Generated Curriculum JSON</CardTitle>
                <CardDescription>
                  Edit the generated curriculum structure and add json_order attributes before saving.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <JsonOutputEditor value={outputJson} onChange={setOutputJson} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="preview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Curriculum Preview</CardTitle>
                <CardDescription>Preview how your curriculum will look to learners.</CardDescription>
              </CardHeader>
              <CardContent>
                <CurriculumRenderer jsonData={outputJson} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default withAuthenticator(CreateCurriculum);
