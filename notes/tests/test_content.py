from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesPage(TestCase):
    """Тесты для страницы списка заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор заметки')
        cls.reader = User.objects.create_user(username='Читатель заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.URL_NOTES_LIST = reverse('notes:list')
        cls.URL_NOTES_ADD = reverse('notes:add')
        cls.URL_NOTES_EDIT = reverse('notes:edit', args=('note-slug',))
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=cls.author,
            slug='note-slug'
        )
        cls.URL_NOTES_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Текст заметки',
                author=cls.author,
                slug=f'note-{index}'
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(all_notes)


    def test_notes_list(self):
        """Тест отображения списка заметок."""
        response = self.author_client.get(self.URL_NOTES_LIST)
        object_list = response.context['object_list']
        first_note = object_list[0]
        object_list = response.context['object_list']
        self.assertIn(object_list[0], object_list)

    def test_notes_list_for_author(self):
        """Тест количества заметок для автора."""
        response = self.author_client.get(self.URL_NOTES_LIST)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, 6)

    def test_notes_list_for_reader(self):
        """Тест количества заметок для другого пользователя."""
        response = self.reader_client.get(self.URL_NOTES_LIST)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEqual(notes_count, 0)

    def test_pages_contain_form(self):
        """Тест наличия формы на страницах редактирования и создания."""
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
