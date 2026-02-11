"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { ChevronDown, ChevronRight, BookOpen, Video, MessageSquare, Database, FileQuestion } from "lucide-react"
import {v4 as uuidv4 } from 'uuid';

import { YoutubeRender } from "./ui/youtube-render"   
import { GoogleSlidesRenderer } from "./ui/google-slides-renderer"
import { TeachersGuide } from "./ui/teachers-guide"

import NEURON_IMAGE from "@/images/neural_network.jpg"


interface CurriculumRendererProps {
  jsonData: string
}

// constants for video rendering
const MAX_WIDTH = 600
const MAX_HEIGHT = 400

export function CurriculumRenderer({ jsonData }: CurriculumRendererProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())

  if (!jsonData.trim()) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <BookOpen className="mx-auto h-12 w-12 mb-4 opacity-50" />
        <p>No curriculum data to preview</p>
        <p className="text-sm">Generate curriculum from the Input JSON tab first</p>
      </div>
    )
  }

  let parsedData
  try {
    parsedData = JSON.parse(jsonData)
  } catch (err) {
    return (
      <div className="text-center py-12 text-destructive">
        <p>Invalid JSON data</p>
        <p className="text-sm">Please check the JSON syntax in the Output JSON tab</p>
      </div>
    )
  }

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId)
    } else {
      newExpanded.add(sectionId)
    }
    setExpandedSections(newExpanded)
  }

  const getResourceIcon = (resourceType: string) => {
    switch (resourceType) {
      case "multimedia":
        return <Video className="h-4 w-4" />
      case "discussion_questions":
        return <MessageSquare className="h-4 w-4" />
      case "datasets":
        return <Database className="h-4 w-4" />
      case "quizzes":
        return <FileQuestion className="h-4 w-4" />
      default:
        return <BookOpen className="h-4 w-4" />
    }
  }

  const renderResource = (resourceType: string, resources: any[]) => {
    return (
      <div key={resourceType} className="space-y-2">
        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
          {getResourceIcon(resourceType)}
          {resourceType.replace("_", " ").toUpperCase()}
        </div>
        <div className="space-y-2 ml-6">
          {resources
            .sort((a, b) => (a.json_order || 0) - (b.json_order || 0))
            .map((resource, index) => (
              <Card key={uuidv4()} className="p-3">
                <div className="space-y-2">
                  {resource.title && <h5 className="text-2xl font-bold">{resource.title}</h5>}
                  {resource.name && <h5 className="font-medium font-bold">{resource.name}</h5>}
                  {resource.description && <p className="text-sm text-muted-foreground">{resource.description}</p>}
                  {(resourceType === "discussion_questions") && (
                    <div className="space-y-1">
                      <div key={uuidv4()} className={`text-sm ${(index % 2 === 0) ? 'flex flex-row' : 'flex flex-row-reverse'}`}>
                        <div className="w-1/2 flex flex-col">
                          <h3 className="text-xl font-bold mb-2">Discussion Question {index + 1}</h3>
                          <p className="text-lg font-medium font-bold mb-2">{resource.question}</p>
                          <p className="text-lg text-muted-foreground">{resource.answer}</p>
                        </div>
                        <div className="w-1/2 p-2">
                          <img className="w-full h-full object-cover rounded-lg" src={NEURON_IMAGE.src} alt="Discussion Question Image" />
                        </div>
                      </div>
                    </div>
                  )}
                  {resource.url && (
                    <a href={resource.url} className="text-blue-600 hover:underline text-sm">
                      {resource.url}
                    </a>
                  )}
                  {resource.video && (
                    <div>
                      <YoutubeRender videoUrl={resource.video} maxHeight={MAX_HEIGHT} maxWidth={MAX_WIDTH} />
                    </div>
                  )}
                  {resource.slide && (
                    <div>
                      <GoogleSlidesRenderer slidesUrl={resource.slide} maxHeight={MAX_HEIGHT} maxWidth={MAX_WIDTH} />
                    </div>
                  )}
                  {resource.teachers_guide && (
                    <div>
                      <TeachersGuide docsUrl={resource.teachers_guide} maxHeight={MAX_HEIGHT} maxWidth={MAX_WIDTH} />
                    </div>
                  )}
                  {resource.question_count && (
                    <p className="text-sm text-muted-foreground">{resource.question_count} questions</p>
                  )}
                </div>
              </Card>
            ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Course Header */}
      <div className="text-center space-y-2 pb-6 border-b">
        <h2 className="text-2xl font-bold">{parsedData.course_title}</h2>
        <p className="text-muted-foreground">Course ID: {parsedData.course_id}</p>
      </div>

      {/* Sections */}
      <div className="space-y-4">
        {parsedData.sections?.map((section: any, sectionIndex: number) => (
          <Card key={section.section_id || sectionIndex}>
            <Collapsible
              open={expandedSections.has(section.section_id)}
              onOpenChange={() => toggleSection(section.section_id)}
            >
              <CollapsibleTrigger asChild>
                <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="text-left">
                      <CardTitle className="flex items-center gap-2">
                        {expandedSections.has(section.section_id) ? (
                          <ChevronDown className="h-4 w-4" />
                        ) : (
                          <ChevronRight className="h-4 w-4" />
                        )}
                        {section.section_title}
                      </CardTitle>
                      <CardDescription>
                        {section.chapters?.length || 0} chapter{section.chapters?.length !== 1 ? "s" : ""}
                      </CardDescription>
                    </div>
                    <Badge variant="secondary">Section {sectionIndex + 1}</Badge>
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <CardContent className="pt-0">
                  {section.chapters?.map((chapter: any, chapterIndex: number) => (
                    <div key={chapterIndex} className="mb-6 last:mb-0">
                      <div className="mb-4">
                        <h4 className="text-xl font-bold mb-2">{chapter.chapter_title}</h4>

                        {chapter.chapter_resources && (
                          <div className="space-y-4 pl-4 border-l-2 border-muted">
                            {Object.entries(chapter.chapter_resources).map(([resourceType, resources]) => {
                              if (Array.isArray(resources) && resources.length > 0) {
                                return renderResource(resourceType, resources)
                              }
                              return null
                            })}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </CollapsibleContent>
            </Collapsible>
          </Card>
        ))}
      </div>
    </div>
  )
}
