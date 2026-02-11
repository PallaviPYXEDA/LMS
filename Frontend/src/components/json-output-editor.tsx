"use client"

import { useState, useEffect } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface JsonOutputEditorProps {
  value: string
  onChange: (value: string) => void
}

export function JsonOutputEditor({ value, onChange }: JsonOutputEditorProps) {
  const [error, setError] = useState<string | null>(null)
  const [isValid, setIsValid] = useState(false)
  const [warnings, setWarnings] = useState<string[]>([])

  useEffect(() => {
    validateOutputJson(value)
  }, [value])

  const validateOutputJson = (jsonString: string) => {
    if (!jsonString.trim()) {
      setError(null)
      setIsValid(false)
      setWarnings([])
      return
    }

    try {
      const parsed = JSON.parse(jsonString)
      const newWarnings: string[] = []

      // Basic structure validation
      if (!parsed.course_id || !parsed.course_title || !parsed.sections) {
        setError("Missing required fields: course_id, course_title, or sections")
        setIsValid(false)
        return
      }

      // Check for json_order attributes
      let hasJsonOrder = false

      if (Array.isArray(parsed.sections)) {
        for (const section of parsed.sections) {
          if (section.chapters && Array.isArray(section.chapters)) {
            for (const chapter of section.chapters) {
              if (chapter.chapter_resources) {
                const resources = chapter.chapter_resources

                // Check each resource type for json_order
                Object.keys(resources).forEach((resourceType) => {
                  if (Array.isArray(resources[resourceType])) {
                    resources[resourceType].forEach((item: any) => {
                      if (item.json_order !== undefined) {
                        hasJsonOrder = true
                      }
                    })
                  }
                })
              }
            }
          }
        }
      }

      if (!hasJsonOrder) {
        newWarnings.push("No json_order attributes found. Add json_order to resources for proper ordering.")
      }

      // Check for activities (commented out in example but should be added)
      let hasActivities = false
      if (Array.isArray(parsed.sections)) {
        for (const section of parsed.sections) {
          if (section.chapters && Array.isArray(section.chapters)) {
            for (const chapter of section.chapters) {
              if (chapter.chapter_resources?.activities) {
                hasActivities = true
                break
              }
            }
          }
        }
      }

      if (!hasActivities) {
        newWarnings.push("No activities found. Consider adding activities to enhance the curriculum.")
      }

      setWarnings(newWarnings)
      setError(null)
      setIsValid(true)
    } catch (err) {
      setError("Invalid JSON syntax")
      setIsValid(false)
      setWarnings([])
    }
  }

  const addJsonOrder = () => {
    if (!value.trim()) return

    try {
      const parsed = JSON.parse(value)

      // Add json_order to resources
      if (Array.isArray(parsed.sections)) {
        parsed.sections.forEach((section: any) => {
          if (section.chapters && Array.isArray(section.chapters)) {
            section.chapters.forEach((chapter: any) => {
              if (chapter.chapter_resources) {
                const resources = chapter.chapter_resources
                let order = 1

                Object.keys(resources).forEach((resourceType) => {
                  if (Array.isArray(resources[resourceType])) {
                    resources[resourceType].forEach((item: any) => {
                      if (item.json_order === undefined) {
                        item.json_order = order++
                      }
                    })
                  }
                })
              }
            })
          }
        })
      }

      onChange(JSON.stringify(parsed, null, 2))
    } catch (err) {
      console.error("Error adding json_order:", err)
    }
  }

  const saveCourse = () => {
    if (isValid) {
      // In a real app, this would save to your backend
      console.log("Saving course:", JSON.parse(value))
      alert("Course saved successfully! (This is a demo)")
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant={isValid ? "default" : value.trim() ? "destructive" : "secondary"}>
            {isValid ? "Valid" : value.trim() ? "Invalid" : "Empty"}
          </Badge>
          {warnings.length > 0 && (
            <Badge variant="outline" className="text-yellow-600">
              {warnings.length} Warning{warnings.length > 1 ? "s" : ""}
            </Badge>
          )}
        </div>
        <div className="flex gap-2">
          <Button className="cursor-pointer bg-blue-500 text-white hover:bg-blue-600" size="sm" onClick={addJsonOrder} disabled={!isValid}>
            Add JSON Order
          </Button>
          <Button className="cursor-pointer bg-blue-500 text-white hover:bg-blue-600" size="sm" onClick={saveCourse} disabled={!isValid}>
            Save Course
          </Button>
        </div>
      </div>

      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Generated curriculum JSON will appear here..."
        className="min-h-96 font-mono text-sm"
        spellCheck={false}
      />

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {warnings.length > 0 && (
        <Alert>
          <AlertDescription>
            <div className="space-y-1">
              <p className="font-medium">Warnings:</p>
              <ul className="list-disc list-inside space-y-1">
                {warnings.map((warning, index) => (
                  <li key={index} className="text-sm">
                    {warning}
                  </li>
                ))}
              </ul>
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}
