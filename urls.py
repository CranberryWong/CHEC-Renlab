from handlers import base, exception, util
from handlers.home import home, news, documents
from handlers.blog import blog
from handlers.auth import auth
from handlers.visualize import visualize
from handlers.aesthetics import main, layoutmain
from handlers.newblog import mainblog

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
            (r"/curriculum_U", documents.CurriculumHandler_U),
            (r"/pastcurriculum", documents.pastcurriculumHandler),
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

            # Layout Experiment
            (r"/layout/statement?", layoutmain.StatementHandler),
            (r"/layout/form", layoutmain.FormHandler),
            (r"/layout/note?", layoutmain.NoteHandler),
            (r"/layout/start/([0-9]+)", layoutmain.WebpageHandler),
            (r"/layout/ratings", layoutmain.RatingHandler),
            (r"/layout/finish", layoutmain.FinishHandler),

            # Visualization
            (r"/visualization", visualize.HomeHandler),
            (r"/visualization/sample?", visualize.MainHandler),

            # New Blog
            (r"/newblog/addreflection", mainblog.AddReflection),
            (r"/newblog/addproject", mainblog.AddProjectHandler),
            (r"/newblog/profileedit", mainblog.ProfileEditHandler),
            (r"/newblog/addactivity",mainblog.AddActivityHandler),
            (r"/newblog/editactivity", mainblog.EditActivityHandler),
            (r"/newblog/deleteactivity", mainblog.DeleteActivity),
            (r"/newblog/addcomment", mainblog.AddCommentHandler),
            (r"/newblog/editcomment", mainblog.EditCommentHandler),
            (r"/newblog/deletecomment",mainblog.DeleteCommentHandler),
            (r"/newblog/addlike", mainblog.AddLikeHandler),
            (r"/newblog/deletelike", mainblog.DeleteLikeHandler),
            (r"/newblog/addreply", mainblog.AddReplyHandler),
            (r"/newblog/editreply", mainblog.EditReplyHandler),
            (r"/newblog/deletereply", mainblog.DeleteReplyHandler),
            (r"/newblog/addlikereply", mainblog.AddReplyLikeHandler),
            (r"/newblog/deletelikereply", mainblog.DeleteReplyLikeHandler),
            (r"/newblog/readnotification", mainblog.ReadNofiticationHandler),
            (r"/newblog/notification", mainblog.NotificationHandler),
            (r"/newblog/(?P<userName>[\w.%]+)", mainblog.MainHandler),
            (r"/newblog/(?P<userName>[\w.%]+)(?:/project)?/?$", mainblog.ViewProjectHandler),
            (r"/newblog/(?P<userName>[\w.%]+)(?:/projectadmin)?/?$", mainblog.ProjectAdminHandler),
            (r"/newblog/(?P<userName>[\w.%]+)(?:/latestblog)?/?$", mainblog.LatestBlogHandler),
            (r"/newblog/(?P<userName>[\w.%]+)(?:/leaderboard)?/?$", mainblog.LeaderboardHandler),

            # i18n
            (r"/language?", base.I18nHandler),

            # 404
            (r".*", exception.ErrorHandler),
    ]
