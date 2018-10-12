from django.contrib import admin
from .models import( Profile,
                    AnswerPaper,
                    Question
                   )


class ProfileAdmin(admin.ModelAdmin):
	list_display = ['title','user', 'institute', 
					'phone_number','position']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'correct_answer', 'question_day']


class AnswerPaperAdmin(admin.ModelAdmin):
    list_display = ['participant', 'answered_q', 'date']


# Register your models here.
admin.site.register(Profile, ProfileAdmin)
admin.site.register(AnswerPaper, AnswerPaperAdmin)
admin.site.register(Question, QuestionAdmin)