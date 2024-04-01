from tkinter import *
import json
from random import randint, shuffle

class Dashboard:
    def __init__(self, scr, icon, button):
        self.scr = scr
        with open("data/dashboard.json", "r") as fin:
            self.dashboard_data = json.load(fin)
        self.all_items = list(list(dic.keys())[0] for dic in self.dashboard_data)
        self.checkboxes = []
        self.generate_answer_list()
        self.answered_correctly = 0
        self.icon = icon
        self.button = button
        self.correct_image = PhotoImage(file="images/true.png")
        self.incorrect_image = PhotoImage(file="images/false.png")
        self.test_passed = False
        self.dashboard_functions = {}
        self.widgets_disabled = False

    
    def generate_answer_list(self):
        self.all_answers = []
        for item in self.dashboard_data:
            item_name = list(item.keys())[0]
            self.all_answers.extend(item[item_name]["Answers"])
        self.all_answers = list(dict.fromkeys(self.all_answers))


    def identify_item(self, e, item):
        if not self.widgets_disabled:
            item_name = str(e.widget).split(".")[2]
            self.correct_answers = []
            self.correct_answers = [item[item_name]["Answers"] for item in self.dashboard_data if list(item.keys())[0] == item_name][0]
            possible_answers = [j for j in self.all_answers if j not in self.correct_answers and j != "is/are functioning"]
            self.displayed_answers = [i for i in self.correct_answers]
            while len(self.displayed_answers) < 4:
                next_answer = possible_answers.pop(randint(0, len(possible_answers) - 1))
                if next_answer not in self.displayed_answers:
                    self.displayed_answers.append(next_answer)
            q_text = f"My {item_name}:"
            self.create_overlay(q_text, "Answer!", [135, 20], lambda: self.get_answers(item_name, e.widget), ("Amazon Ember Display Light", 18, "bold"))
            spacing = 150
            shuffle(self.displayed_answers)
            self.displayed_answers = {i:IntVar() for i in self.displayed_answers}
            for answer in self.displayed_answers:
                check = Checkbutton(self.dashboard, text=answer, variable=self.displayed_answers[answer], bg="bisque", onvalue=1, offvalue=0, font=("Amazon Ember Display Light", 9, "bold"))
                check.place(x=375, y=spacing)
                spacing += 30
                self.checkboxes.append(check)
            e.widget.unbind("<Button-1>", self.dashboard_functions[item_name][0])
            for item in self.dashboard_data:
                if list(item.keys())[0] == item_name:
                    item[item_name]["Answered"] = True
            self.widgets_disabled = True
        #print([item[item_name]["Answered"] for item in self.dashboard_data if list(item.keys())[0] == item_name][0])
        

    def create_overlay(self, textual_matter, button_text, coords, cmd, font=None, answers=None):
        self.question_overlay = Canvas(self.dashboard, width=300, height=300, bg="bisque")
        self.question_text = self.question_overlay.create_text(coords[0], coords[1], text=textual_matter, font=font, width=275)
        self.question_overlay.place(x=350, y=100)
        self.answer_button = Button(self.dashboard, text=button_text)
        self.answer_button.place(x=465, y=330)
        self.answer_button.config(command=cmd)


    def hide_instructions(self):
        self.question_overlay.destroy()
        self.answer_button.destroy()

    
    def get_answers(self, name, widget):
        answered = [item[list(item.keys())[0]]["Answered"] for item in self.dashboard_data]
        answered_answers = [i["text"] for i in self.checkboxes if self.displayed_answers[i["text"]].get() ==1]
        if sorted(answered_answers) == sorted(self.correct_answers):
            self.answered_correctly += 1
            self.score_label.config(text=f"Correct answers: {self.answered_correctly}")
            widget.create_image(0, 0, anchor=NW, image=self.correct_image)
        else:
            widget.create_image(0, 0, anchor=NW, image=self.incorrect_image)
        for i in self.checkboxes:
            i.destroy()
        self.checkboxes = []
        self.widgets_disabled = False
        self.hide_instructions()
        if False not in answered:
            self.finished_message = f"""
        Congratulations, you have finished the
        first part of the in-cab pre-trip inspection.

        You answered {self.answered_correctly} out of 14 questions
        correctly.
        """
            if self.answered_correctly / 14 > 0.8:
                self.test_passed = True
            self.create_overlay(self.finished_message, "Continue Test", [150, 120], lambda: self.dashboard.destroy(), ("Amazon Ember", 9, "normal"))
            self.button.config(state=DISABLED)


    def display_instructions(self):
        self.create_overlay(open("data/dashboard_instructions.txt").read(), "Start test!", [150, 120], self.hide_instructions, ("Amazon Ember", 9, "normal"))


    def get_result(self):
            return self.test_passed            


    def display_dashboard(self):
        self.dashboard = Toplevel(self.scr)
        self.dashboard.geometry("1024x770")
        self.dashboard.title("In-Cab Pretrip Inspection - Dashboard")
        self.dashboard.iconbitmap(self.icon)
        self.dash_image = PhotoImage(file="images/FM_instrument_cluster.png")
        self.dash_bg = Canvas(self.dashboard, width=1024, height=770)
        self.dash_bg.pack(expand=1, fill=BOTH)
        self.dashboard_items = []
        for item in self.dashboard_data:
            item_name = list(item.keys())[0]
            dashboard_item = Canvas(self.dashboard, width=item[item_name]["Width/Height"][0], height=item[item_name]["Width/Height"][1], name=item[item_name]["Name"], highlightbackground="gold", highlightthickness=3)
            item_image = PhotoImage(file=item[item_name]["Image"])
            dashboard_item.place(x=item[item_name]["Coords"][0], y=item[item_name]["Coords"][1])
            item_tag = dashboard_item.create_image(0, 0, anchor=NW, image=item_image, state=NORMAL)
            item_func = dashboard_item.tag_bind(item_tag, "<Button-1>", lambda e: self.identify_item(e, dashboard_item))
            #I use the dashboard_functions dictionary to store the functions bound to each item so they can be disabled later.
            #I store the images here as well for no reason other than that, without storing them somehow, the garbage collector
            #will delete each of them after it thinks they're no longer used. Instead of storing them in a separate list, I decided
            #to store them in this dictionary to save a few lines of code (while simultaneously creating a need for this lengthy comment)
            self.dashboard_functions.update({item_name: [item_func, item_tag, item_image]})
            self.dashboard_items.append(dashboard_item)
        self.score_label = Label(self.dashboard, text=f"Correct answers: {self.answered_correctly}", font=("Amazon Ember Display Heavy", 20, "bold"), fg="red", bg="black")
        self.score_label.place(x=80, y=135)
        self.dash_bg.create_image(0, 0, anchor=NW, image=self.dash_image)
        self.display_instructions()

        self.dashboard.mainloop()