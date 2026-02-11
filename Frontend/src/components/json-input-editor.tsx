"use client"

import { useState, useEffect } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface JsonInputEditorProps {
  value: string
  onChange: (value: string) => void
  onValidationChange?: (isValid: boolean) => void
}

const defaultInputJson = {
  course_id: "course_001",
  course_title: "Intro to Data Science",
  sections: [
    {
      section_id: "sec_1",
      section_title: "Foundations",
      file_ids: ["file_101", "file_102"],
    },
    {
      section_id: "sec_2",
      section_title: "Machine Learning",
      file_ids: ["file_201"],
    },
  ],
}

export function JsonInputEditor({ value, onChange, onValidationChange }: JsonInputEditorProps) {
  const [error, setError] = useState<string | null>(null)
  const [isValid, setIsValid] = useState(false)

  useEffect(() => {
    validateJson(value)
  }, [value])

  const validateJson = (jsonString: string) => {
    if (!jsonString.trim()) {
      setError(null)
      setIsValid(false)
      onValidationChange?.(false)
      return
    }

    try {
      const parsed = JSON.parse(jsonString)

      // Validate required fields
      if (!parsed.course_id || !parsed.course_title || !parsed.sections) {
        setError("Missing required fields: course_id, course_title, or sections")
        setIsValid(false)
        onValidationChange?.(false)
        return
      }

      if (!Array.isArray(parsed.sections)) {
        setError("Sections must be an array")
        setIsValid(false)
        onValidationChange?.(false)
        return
      }

      // Validate each section
      for (const section of parsed.sections) {
        if (!section.section_id || !section.section_title || !section.file_ids) {
          setError("Each section must have section_id, section_title, and file_ids")
          setIsValid(false)
          onValidationChange?.(false)
          return
        }

        if (!Array.isArray(section.file_ids)) {
          setError("file_ids must be an array")
          setIsValid(false)
          onValidationChange?.(false)
          return
        }
      }

      setError(null)
      setIsValid(true)
      onValidationChange?.(true)
    } catch (err) {
      setError("Invalid JSON syntax")
      setIsValid(false)
      onValidationChange?.(false)
    }
  }

  const loadExample = () => {
    onChange(JSON.stringify(defaultInputJson, null, 2))
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant={isValid ? "default" : value.trim() ? "destructive" : "secondary"}>
            {isValid ? "Valid" : value.trim() ? "Invalid" : "Empty"}
          </Badge>
          {value.trim() && <span className="text-sm text-muted-foreground">{value.split("\n").length} lines</span>}
        </div>
        <Button className="hover:cursor-pointer bg-blue-500 text-white hover:bg-blue-600" variant="secondary" size="sm" onClick={loadExample}>
          Load Example
        </Button>
      </div>

      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter your course structure JSON here..."
        className="min-h-96 font-mono text-sm"
        spellCheck={false}
      />

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="text-xs text-muted-foreground space-y-1">
        <p>
          <strong>Required structure:</strong>
        </p>
        <ul className="list-disc list-inside space-y-1 ml-2">
          <li>
            <code>course_id</code>: Unique identifier for the course
          </li>
          <li>
            <code>course_title</code>: Display name for the course
          </li>
          <li>
            <code>sections</code>: Array of course sections
          </li>
          <li>
            Each section needs: <code>section_id</code>, <code>section_title</code>, <code>file_ids[]</code>
          </li>
        </ul>
      </div>
    </div>
  )
}
