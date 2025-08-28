from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты создания заметки."""

    @classmethod
    def setUpTestData(cls):
        """Создание пользователя и подготовка данных для тестов."""
        cls.author = User.objects.create_user(username='Крокодил Гена')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.url = reverse('notes:add', args=None)
        cls.form_data = {
            'title': 'Заметка',
            'text': 'Текст заметки',
        }
        cls.notes_count = Note.objects.count()

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.notes_count)  

    def test_user_can_create_note(self):
        """Пользователь может создать заметку."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, '/done/')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)


class TestNoteEditDelete(TestCase):
    """Тесты создания заметки."""

    @classmethod
    def setUpTestData(cls):
        """Создание пользователя и подготовка данных для тестов."""
        cls.author = User.objects.create_user(username='Крокодил Гена')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Заметка',
            'text': 'Текст заметки',
        }
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            author=cls.author,
            slug='test-slug'
        )

    def test_note_slug_is_unique(self):
        """Проверка уникальности slug заметки."""
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(self.url, data=self.form_data)
        response = response.render()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context['form']
        self.assertFormError(
            form,
            'slug',
            self.note.slug + WARNING
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Если slug не передан — он генерируется автоматически."""
        form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
        }
        self.auth_client.post(self.url, data=form_data)
        self.assertEqual(Note.objects.count(), 2)
        self.assertTrue(Note.objects.exclude(slug='test-slug').exists())

    def test_anonymous_user_cant_edit_note(self):
        """Анонимный пользователь не может редактировать заметку."""
        response = self.client.post(
            reverse('notes:edit', args=(self.note.slug,)),
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_edit_note(self):
        """Пользователь может редактировать заметку."""
        response = self.auth_client.post(
            reverse('notes:edit', args=(self.note.slug,)),
            data=self.form_data
        )
        self.assertRedirects(response, '/done/')
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(Note.objects.count(), 1)

    def test_anonymous_user_cant_delete_note(self):
        """Анонимный пользователь не может удалить заметку."""
        response = self.client.post(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_delete_note(self):
        """Пользователь может удалить заметку."""
        response = self.auth_client.post(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertRedirects(response, '/done/')
        self.assertEqual(Note.objects.count(), 0)
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(slug=self.note.slug)
