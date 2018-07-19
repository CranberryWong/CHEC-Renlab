from handlers import base, exception, util
from handlers.home import home, news, documents
from handlers.blog import blog
from handlers.auth import auth

from handlers.aesthetics import main

handlers = [
            # Home
            (r"/", home.HomeHandler),
            (r"/members", home.MembersHandler),
            (r"/news", news.NewsHandler),
            (r"/news/(.*)", news.NewsShowHandler),
            (r"/facilities", documents.FacilitesHandler),
            (r"/intro", documents.IntroHandler),
            (r"/projects", documents.ProjectsHandler),
            (r"/projects/(.*)", documents.ProjectShowHandler),
            (r"/publication", documents.PubHandler),
            (r"/curriculum", documents.CurriculumHandler),            
            (r"/resource", documents.ResourceHandler),

            # Auth
            (r"/signin", auth.SignInHandler),
            (r"/signout", auth.SignOutHandler),

            # Blog
            (r"/blog/([\w./?%&=]*)?", blog.BlogHandler),
            (r"/blogwriting?", blog.BlogWritingHandler),
            (r"/profile/([\w./?%&=]*)", blog.ProfileHandler),
            (r"/blogcontent?", blog.BlogContentHandler),
            (r"/blogdeleting?", blog.BlogDeletingHandler),
            (r"/blogrevising?", blog.BlogRevisingHandler),
            (r"/profilewriting?", blog.ProfileEditingHandler),
            (r"/profilerequest", blog.ProfileRequestHandler),
            (r"/passwordchanging", blog.PasswordChangeHandler),
            (r"/customlinkchanging", blog.CustomLinkHandler),

            # Experiment
            (r"/experiment", main.MainHandler),
            (r"/aesthetic/statement", main.StatementHandler),
            (r"/aesthetic/form", main.FormHandler),
            (r"/aesthetic/note?", main.NoteHandler),
            (r"/aesthetic/start/([0-9]+)", main.WebpageHandler),
            (r"/aesthetic/ratings", main.RatingHandler),
            (r"/aesthetic/finish", main.FinishHandler),

            # i18n
            (r"/language?", base.I18nHandler),

            # 404
            (r".*", exception.ErrorHandler),

    ]