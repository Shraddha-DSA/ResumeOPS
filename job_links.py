import urllib.parse

def get_job_links(job_role):
    query = urllib.parse.quote(job_role)

    links = [
        {
            "platform": "LinkedIn Jobs",
            "url": f"https://www.linkedin.com/jobs/search/?keywords={query}"
        },
        {
            "platform": "Indeed",
            "url": f"https://www.indeed.com/jobs?q={query}"
        },
        {
            "platform": "Wellfound (AngelList)",
            "url": f"https://wellfound.com/jobs?query={query}"
        }
    ]

    return links
