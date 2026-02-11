import { withAuthenticator } from "@aws-amplify/ui-react"
import { BookOpen, Plus, Users, BarChart3 } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"


function Homepage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="bg-primary text-primary-foreground py-6 px-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold tracking-tight">Curriculum Management Platform</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Create New Curriculum Tile */}
          <Link href="/create-curriculum">
            <Card className="h-full hover:shadow-lg transition-all duration-300 hover:scale-105 cursor-pointer group">
              <CardHeader className="text-center pb-4">
                <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <Plus className="w-8 h-8 text-primary" />
                </div>
                <CardTitle className="text-xl">Create New Curriculum</CardTitle>
                <CardDescription>
                  Build a new curriculum from scratch using our JSON-based structure editor
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                <Button className="w-full" size="lg">
                  Start Creating
                </Button>
                <div className="mt-4 flex items-center justify-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <BookOpen className="w-4 h-4" />
                    <span>JSON Editor</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <BarChart3 className="w-4 h-4" />
                    <span>Live Preview</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
          {/* View Existing Curricula Tile */}
          <Link href="/curricula">
            <Card className="h-full hover:shadow-lg transition-all duration-300 hover:scale-105 cursor-pointer group">
              <CardHeader className="text-center pb-4">
                <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <BookOpen className="w-8 h-8 text-primary" />
                </div>
                <CardTitle className="text-xl">View Existing Curricula</CardTitle>
                <CardDescription>Browse and manage your previously created curriculum content</CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                <Button className="w-full" size="lg">
                  Browse Curricula
                </Button>
                <div className="mt-4 flex items-center justify-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    <span>Manage Content</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <BarChart3 className="w-4 h-4" />
                    <span>View Analytics</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>
      </main>
    </div>
  )
}

export default withAuthenticator(Homepage);
