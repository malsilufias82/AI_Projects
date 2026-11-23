<template>
  <q-page class="home-page">
    <div class="home-container">
      <!-- Left Column -->
      <!-- <div class=""> -->
        <q-scroll-area class="column-scroll left-column" :thumb-style="{width: '5px'}">
          <div class="column-content">
            <!-- Highlights Card -->
            <q-expansion-item
              class="q-mb-md bg-white"
              default-opened
            >
              <template v-slot:header>
                <q-item-section avatar>
                  <q-avatar icon="cake" color="orange-1" text-color="orange" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-subtitle1 text-bold">Today's Celebrations</q-item-label>
                  <q-item-label caption>{{ highlights.length }} celebrations</q-item-label>
                </q-item-section>
              </template>
              <q-card-section class="q-pt-none">
                <div v-for="highlight in highlights" :key="highlight.name" class="highlight-item">
                  <q-avatar size="32px">
                    <img :src="highlight.avatar" />
                  </q-avatar>
                  <div class="q-ml-sm">
                    <div class="text-subtitle2">{{ highlight.name }}</div>
                    <div class="text-caption text-grey-6">
                      <span v-if="highlight.type === 'birthday'">Happy Birthday 🎂</span>
                      <span v-else-if="highlight.type === 'work_anniversary'">{{ highlight.years }} years work anniversary 🎉</span>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-expansion-item>

            <!-- Wall of Fame Card -->
            <q-expansion-item
              class="q-mb-md bg-white"
              default-opened
            >
              <template v-slot:header>
                <q-item-section avatar>
                  <q-avatar icon="emoji_events" color="orange-1" text-color="orange" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-subtitle1 text-bold">Wall of Fame</q-item-label>
                  <q-item-label caption>{{ wallOfFame.length }} members</q-item-label>
                </q-item-section>
              </template>
              <q-card-section class="q-pa-sm">
                <div v-for="member in wallOfFame" :key="member.name" class="fame-item">
                  <q-avatar size="32px">
                    <img :src="member.avatar" />
                  </q-avatar>
                  <div class="q-ml-sm">
                    <div class="text-subtitle2">{{ member.name }}</div>
                    <div class="text-caption text-grey-6">{{ member.title }}</div>
                  </div>
                </div>
              </q-card-section>
            </q-expansion-item>

            <!-- People on Leave Card -->
            <q-expansion-item
              class="q-mb-md bg-white"
              default-opened
            >
              <template v-slot:header>
                <q-item-section avatar>
                  <q-avatar icon="flight_takeoff" color="orange-1" text-color="orange" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-subtitle1 text-bold">People on Leave</q-item-label>
                  <q-item-label caption>{{ peopleOnLeave.length }} on leave</q-item-label>
                </q-item-section>
              </template>
              <q-card-section class="q-pt-none">
                <q-select
                  v-model="leaveFilter"
                  :options="leaveFilterOptions"
                  label="Filter by Team"
                  outlined
                  dense
                  class="q-mb-sm"
                />
                <div v-for="person in peopleOnLeave" :key="person.name" class="leave-item">
                  <q-avatar size="32px">
                    <img :src="person.avatar" />
                  </q-avatar>
                  <div class="q-ml-sm">
                    <div class="text-subtitle2">{{ person.name }}</div>
                    <div class="text-caption text-grey-6">{{ person.dates }}</div>
                  </div>
                </div>
              </q-card-section>
            </q-expansion-item>

            <!-- Upcoming Events Card -->
            <q-expansion-item
              class="q-mb-md bg-white"
              default-opened
            >
              <template v-slot:header>
                <q-item-section avatar>
                  <q-avatar icon="event" color="orange-1" text-color="orange" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-subtitle1 text-bold">Upcoming Events</q-item-label>
                  <q-item-label caption>{{ upcomingEvents.length }} events</q-item-label>
                </q-item-section>
              </template>
              <q-card-section class="q-pt-none">
                <div v-for="event in upcomingEvents" :key="event.title" class="event-item">
                  <q-icon :name="event.icon" :color="event.color" />
                  <div class="q-ml-sm">
                    <div class="text-subtitle2">{{ event.title }}</div>
                    <div class="text-caption text-grey-6">{{ event.datetime }}</div>
                  </div>
                </div>
              </q-card-section>
            </q-expansion-item>
          </div>
        </q-scroll-area>
      <!-- </div> -->

      <!-- Center Column -->
      <div class="center-column">
        <div class="column-content">
          <!-- Post Creation -->
          <q-card class="q-mb-md">
            <q-card-section>
              <q-input
                v-model="newPost"
                placeholder="What's on your mind?"
                outlined
                autogrow
                rows="3"
              />
            </q-card-section>
            <q-card-actions align="right">
              <q-btn flat color="primary" label="Post" @click="createPost" />
            </q-card-actions>
          </q-card>

          <!-- Post Feed -->
          <div v-for="post in posts" :key="post.id" class="q-mb-md">
            <q-card>
              <q-card-section>
                <div class="flex items-center">
                  <q-avatar size="40px">
                    <img :src="post.avatar" />
                  </q-avatar>
                  <div class="q-ml-sm">
                    <div class="text-subtitle1">{{ post.author }}</div>
                    <div class="text-caption text-grey-6">{{ post.time }}</div>
                  </div>
                </div>
              </q-card-section>
              <q-card-section>
                <div class="text-body1">{{ post.content }}</div>
              </q-card-section>
              <q-card-section v-if="post.image" class="q-pa-none">
                <q-img :src="post.image" :ratio="16/9" />
              </q-card-section>
              <q-card-actions>
                <q-btn flat round dense :icon="post.liked ? 'favorite' : 'favorite_border'"
                      :color="post.liked ? 'red' : 'grey'" @click="toggleLike(post)" />
                <span class="text-caption">{{ post.likes }}</span>
                <q-btn flat round dense icon="comment" color="grey" class="q-ml-md" />
                <span class="text-caption">{{ post.comments }}</span>
                <q-space />
                <q-btn flat round dense icon="share" color="grey" />
              </q-card-actions>
            </q-card>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <!-- <div class=""> -->
        <q-scroll-area class="column-scroll right-column" :thumb-style="{width: '5px'}">
          <div class="column-content">
            <!-- Today's Work Done -->
            <q-card class="q-mb-md">
              <q-card-section class="q-px-md q-py-sm">
                <div class="text-subtitle1 text-bold">Today's Work Done</div>
              </q-card-section>
              <q-card-section class="q-pt-none">
                <q-editor
                  v-model="workDone"
                  min-height="150px"
                  :toolbar="[
                    ['bold', 'italic', 'strike', 'underline'],
                    ['unordered', 'ordered'],
                    ['link']
                  ]"
                />
              </q-card-section>
            </q-card>

            <!-- Inbox -->
            <q-card class="q-mb-md">
              <q-card-section class="q-px-md q-py-sm">
                <div class="text-subtitle1 text-bold">Inbox</div>
              </q-card-section>
              <q-list separator>
                <q-item clickable>
                  <q-item-section avatar>
                    <q-avatar color="primary" text-color="white">A</q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>Admin Team</q-item-label>
                    <q-item-label caption>New policy update</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-badge color="red" floating>2</q-badge>
                  </q-item-section>
                </q-item>
                <q-item clickable>
                  <q-item-section avatar>
                    <q-avatar color="green" text-color="white">HR</q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label>HR Department</q-item-label>
                    <q-item-label caption>Leave approved</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-card>

            <!-- Calendar -->
            <q-card v-show="true" class="q-mb-md">
              <q-card-section class="q-px-md q-py-sm">
                <div class="text-subtitle1 text-bold">Calendar</div>
              </q-card-section>
              <q-card-section class="q-pa-none">
                <q-date v-model="selectedDate" minimal class="no-shadow" />
              </q-card-section>
            </q-card>

            <!-- Leave Balance -->
            <q-card class="q-mb-md">
              <q-card-section class="q-px-md q-py-sm">
                <div class="text-subtitle1 text-bold">Leave Balance</div>
              </q-card-section>
              <q-card-section>
                <div class="leave-balance-item">
                  <div class="text-subtitle2">Annual Leave</div>
                  <div class="text-h6 text-primary">12 days</div>
                </div>
                <q-separator class="q-my-sm" />
                <div class="leave-balance-item">
                  <div class="text-subtitle2">Sick Leave</div>
                  <div class="text-h6 text-positive">5 days</div>
                </div>
                <q-separator class="q-my-sm" />
                <div class="leave-balance-item">
                  <div class="text-subtitle2">Personal Leave</div>
                  <div class="text-h6 text-warning">3 days</div>
                </div>
              </q-card-section>
            </q-card>

            <q-card class="q-mb-md">
              <q-card-section class="q-px-md q-py-sm">
                <div class="text-subtitle1 text-bold">Holiday List</div>
                <div class="text-caption text-grey-6">{{ holidayYear }}</div>
              </q-card-section>
              <q-card-section class="q-pa-none">
                <q-table
                  :rows="holidays"
                  :columns="holidayColumns"
                  row-key="date"
                  :loading="holidaysLoading"
                  flat
                  dense
                  hide-bottom
                  :pagination="{ rowsPerPage: 0 }"
                  no-data-label="No holidays available for this year"
                >
                  <template v-slot:body-cell-date_day="props">
                    <q-td :props="props">{{ formatHolidayDate(props.row) }}</q-td>
                  </template>
                </q-table>
                <q-banner v-if="holidayError" class="bg-red-1 text-negative q-ma-sm" rounded>
                  {{ holidayError }}
                </q-banner>
              </q-card-section>
            </q-card>
          </div>
        </q-scroll-area>
      <!-- </div> -->
    </div>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from 'boot/axios'

const leaveFilter = ref('All Teams')
const leaveFilterOptions = ['All Teams', 'Engineering', 'Marketing', 'HR', 'Sales']

const newPost = ref('')
const workDone = ref('')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const holidayYear = new Date().getFullYear()
const holidays = ref([])
const holidaysLoading = ref(false)
const holidayError = ref('')
const holidayColumns = [
  { name: 'holiday_name', label: 'Holiday Name', field: 'holiday_name', align: 'left' },
  { name: 'date_day', label: 'Date (Day)', field: 'date', align: 'left' }
]

const formatHolidayDate = (holiday) => {
  const date = new Date(`${holiday.date}T00:00:00`)
  const formattedDate = new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  }).format(date)
  return `${formattedDate} (${holiday.day})`
}

const loadHolidays = async () => {
  holidaysLoading.value = true
  holidayError.value = ''
  try {
    const response = await api.get('/v1/holidays', { params: { year: holidayYear } })
    holidays.value = response.data
  } catch (error) {
    holidayError.value = error.response?.data?.detail || 'Could not load the holiday list.'
  } finally {
    holidaysLoading.value = false
  }
}

onMounted(loadHolidays)

const highlights = ref([
  {
    name: 'John Doe',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    type: 'birthday'
  },
  {
    name: 'Jane Smith',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    type: 'work_anniversary',
    years: 3
  }
])

const wallOfFame = ref([
  {
    name: 'John Doe',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    title: 'Employee of the Month'
  },
  {
    name: 'Jane Smith',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    title: 'Top Performer'
  }
])

const peopleOnLeave = ref([
  {
    name: 'Mike Johnson',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    dates: 'Jul 15 - Jul 20'
  },
  {
    name: 'Sarah Williams',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    dates: 'Jul 18 - Jul 22'
  }
])

const upcomingEvents = ref([
  {
    icon: 'event',
    color: 'primary',
    title: 'Team Meeting',
    datetime: 'Jul 20, 10:00 AM'
  },
  {
    icon: 'celebration',
    color: 'primary',
    title: 'Company Anniversary',
    datetime: 'Jul 25, 3:00 PM'
  }
])

const posts = ref([
  {
    id: 1,
    author: 'John Doe',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    time: '2 hours ago',
    content: 'Just completed the new feature implementation! 🎉',
    image: 'https://picsum.photos/800/400?random=1',
    likes: 15,
    comments: 3,
    liked: false
  },
  {
    id: 2,
    author: 'Jane Smith',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    time: '4 hours ago',
    content: 'Great team meeting today. Excited about the upcoming projects!',
    likes: 23,
    comments: 7,
    liked: true
  },
  {
    id: 3,
    author: 'Mike Johnson',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    time: '6 hours ago',
    content: 'Thanks everyone for the support on the migration project.',
    image: 'https://picsum.photos/800/400?random=2',
    likes: 31,
    comments: 12,
    liked: false
  },
  {
    id: 4,
    author: 'Sarah Williams',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    time: '8 hours ago',
    content: 'Looking forward to the company retreat next week! 🏖️',
    likes: 45,
    comments: 8,
    liked: true
  },
  {
    id: 5,
    author: 'David Brown',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    time: '10 hours ago',
    content: 'New code review process is working great. Much more efficient now!',
    image: 'https://picsum.photos/800/400?random=3',
    likes: 28,
    comments: 5,
    liked: false
  },
  {
    id: 6,
    author: 'Emily Davis',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    time: '12 hours ago',
    content: 'Just finished the quarterly report. Numbers are looking good! 📊',
    likes: 52,
    comments: 15,
    liked: true
  },
  {
    id: 7,
    author: 'Chris Wilson',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    time: '1 day ago',
    content: 'Great collaboration with the design team on the new UI components.',
    image: 'https://picsum.photos/800/400?random=4',
    likes: 19,
    comments: 4,
    liked: false
  },
  {
    id: 8,
    author: 'Amanda Taylor',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    time: '1 day ago',
    content: 'Thanks to everyone who helped with the client presentation yesterday! 🙏',
    likes: 67,
    comments: 22,
    liked: true
  },
  {
    id: 9,
    author: 'Robert Martinez',
    avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
    time: '2 days ago',
    content: 'The new API documentation is now live. Check it out!',
    image: 'https://picsum.photos/800/400?random=5',
    likes: 34,
    comments: 9,
    liked: false
  },
  {
    id: 10,
    author: 'Jennifer Lee',
    avatar: 'https://cdn.quasar.dev/img/girl-avatar.png',
    time: '2 days ago',
    content: 'Celebrating 5 years at the company today! Time flies when you\'re having fun 🎂',
    likes: 89,
    comments: 31,
    liked: true
  }
])

const createPost = () => {
  if (newPost.value.trim()) {
    posts.value.unshift({
      id: Date.now(),
      author: 'You',
      avatar: 'https://cdn.quasar.dev/img/boy-avatar.png',
      time: 'Just now',
      content: newPost.value,
      likes: 0,
      comments: 0,
      liked: false
    })
    newPost.value = ''
  }
}

const toggleLike = (post) => {
  post.liked = !post.liked
  post.likes += post.liked ? 1 : -1
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.home-container {
  display: flex;
  gap: 12px;
  padding: 0px 16px;
  max-width: 1600px;
  margin: 0 auto;
}

.q-card, .q-expansion-item {
  background: white;
  box-shadow: none;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
}

.left-column {
  flex: 0 0 300px;
  /* position: sticky; */
  /* top: 64px; */
  /* height: calc(100vh - 80px); */
}

.center-column {
  flex: 1;
}

.right-column {
  flex: 0 0 300px;
  /* position: sticky; */
  /* top: 64px; */
  /* height: calc(100vh - 80px); */
}

.column-scroll {
  height: calc(100vh - 50px);
  position: sticky;
  top: 50px;
  scrollbar-width: 0px;
}

.column-content {
  padding: 20px 0px;
  padding-right: 12px;
}

.highlight-item,
.fame-item,
.leave-item,
.event-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.highlight-item:last-child,
.fame-item:last-child,
.leave-item:last-child,
.event-item:last-child {
  border-bottom: none;
}
.leave-balance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

@media (max-width: 1200px) {
  .home-container {
    flex-direction: column;
  }

  .left-column,
  .right-column {
    flex: none;
    width: 100%;
    position: static;
    height: auto;
  }

  .center-column {
    max-width: 100%;
  }

}
</style>
