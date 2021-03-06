from kivy.uix.scatter import ScatterPlane
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.layout import Layout
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.app import App
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView


class PlaygroundDragElement(BoxLayout):

    playground = ObjectProperty()
    target = ObjectProperty(allownone=True)
    can_place = BooleanProperty(False)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center_x = touch.x
            self.y = touch.y + 20
            self.target = self.playground.try_place_widget(
                    self.children[0], self.center_x, self.y - 20)
            self.can_place = self.target is not None
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.target = self.playground.try_place_widget(
                    self.children[0], self.center_x, self.y - 20)
            self.can_place = self.target is not None
            if self.can_place:
                child = self.children[0]
                child.parent.remove_widget(child)
                self.playground.place_widget(
                        child, self.center_x, self.y - 20)
            self.parent.remove_widget(self)
            return True


class Playground(ScatterPlane):

    root = ObjectProperty()
    selection_mode = BooleanProperty(True)

    def try_place_widget(self, widget, x, y):
        x, y = self.to_local(x, y)
        return self.find_target(x, y, self.root, widget)

    def place_widget(self, widget, x, y):
        x, y = self.to_local(x, y)
        target = self.find_target(x, y, self.root, widget)
        #wx, wy = target.to_widget(x, y)
        #widget.pos = wx, wy
        widget.pos = 0, 0
        target.add_widget(widget)

    def find_target(self, x, y, target, widget=None):
        if not target.collide_point(x, y):
            return None
        x, y = target.to_local(x, y)
        for child in target.children:
            if not child.collide_point(x, y):
                continue
            if not self.allowed_target_for(child, widget):
                continue
            return self.find_target(x, y, child, widget)
        return target

    def allowed_target_for(self, target, widget):
        # stop on complex widget
        t = target if widget else target.parent
        if isinstance(t, FileChooserListView):
            return False
        if isinstance(t, FileChooserIconView):
            return False

        # if we don't have widget, always return true
        if widget is None:
            return True

        is_widget_layout = isinstance(widget, Layout)
        is_target_layout = isinstance(target, Layout)
        if is_widget_layout and is_target_layout:
            return True
        if is_target_layout:
            return True
        return False

    def on_touch_down(self, touch):
        if self.selection_mode:
            if super(ScatterPlane, self).collide_point(*touch.pos):
                x, y = self.to_local(*touch.pos)
                target = self.find_target(x, y, self.root)
                App.get_running_app().focus_widget(target)
                return True
        return super(Playground, self).on_touch_down(touch)
