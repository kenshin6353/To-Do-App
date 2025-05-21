import { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  AppBar,
  Toolbar,
} from '@mui/material';
import { Delete as DeleteIcon, Edit as EditIcon, Add as AddIcon } from '@mui/icons-material';
import { taskApi, notificationApi } from '../services/api';

function Dashboard({ token, onLogout }) {
  const [tasks, setTasks] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [taskForm, setTaskForm] = useState({
    title: '',
    description: '',
    due_date: '',
  });

  useEffect(() => {
    fetchTasks();
    fetchNotifications();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await taskApi.getTasks(token);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const fetchNotifications = async () => {
    try {
      const response = await notificationApi.getNotifications(token);
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const handleOpenDialog = (task = null) => {
    if (task) {
      setEditingTask(task);
      setTaskForm({
        title: task.title,
        description: task.description,
        due_date: task.due_date.slice(0, 16), // trim to 'YYYY-MM-DDTHH:mm'
      });
    } else {
      setEditingTask(null);
      setTaskForm({
        title: '',
        description: '',
        due_date: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingTask(null);
    setTaskForm({
      title: '',
      description: '',
      due_date: '',
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // ✅ Ensure due_date includes seconds for Python compatibility
    const paddedDueDate =
      taskForm.due_date.length === 16 ? `${taskForm.due_date}:00` : taskForm.due_date;

    const formData = {
      ...taskForm,
      due_date: paddedDueDate,
    };

    try {
      if (editingTask) {
        await taskApi.updateTask(editingTask.id, formData, token);
      } else {
        await taskApi.createTask(formData, token);
      }
      handleCloseDialog();
      fetchTasks();
    } catch (error) {
      console.error('Error saving task:', error);
    }
  };

  const handleDelete = async (taskId) => {
    try {
      await taskApi.deleteTask(taskId, token);
      fetchTasks();
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Todo App
          </Typography>
          <Button color="inherit" onClick={onLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
          <Typography variant="h4">My Tasks</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Add Task
          </Button>
        </Box>

        <List>
          {tasks.map((task) => (
            <ListItem
              key={task.id}
              sx={{
                mb: 2,
                bgcolor: 'background.paper',
                borderRadius: 1,
                boxShadow: 1,
              }}
            >
              <ListItemText
                primary={task.title}
                secondary={
                  <>
                    <Typography component="span" variant="body2">
                      {task.description}
                    </Typography>
                    <br />
                    <Typography component="span" variant="body2" color="text.secondary">
                      Due: {new Date(task.due_date).toLocaleString()}
                    </Typography>
                  </>
                }
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => handleOpenDialog(task)}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDelete(task.id)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>

        <Dialog open={openDialog} onClose={handleCloseDialog}>
          <DialogTitle>{editingTask ? 'Edit Task' : 'Add New Task'}</DialogTitle>
          <DialogContent>
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Title"
                name="title"
                value={taskForm.title}
                onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
                margin="normal"
                required
              />
              <TextField
                fullWidth
                label="Description"
                name="description"
                value={taskForm.description}
                onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
                margin="normal"
                multiline
                rows={3}
              />
              <TextField
                fullWidth
                label="Due Date"
                name="due_date"
                type="datetime-local"
                value={taskForm.due_date}
                onChange={(e) => setTaskForm({ ...taskForm, due_date: e.target.value })}
                margin="normal"
                required
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button onClick={handleSubmit} variant="contained">
              {editingTask ? 'Update' : 'Add'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}

export default Dashboard;
