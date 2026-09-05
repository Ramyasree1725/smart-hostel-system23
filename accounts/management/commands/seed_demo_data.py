import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from resources.models import ResourceCategory, Resource, AvailabilityRule
from bookings.models import Booking

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds 16 demo resources with images, availability rules, and active bookings'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with expanded 16-facility demo data...')

        # 1. Users
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@booking.local',
                'first_name': 'System',
                'last_name': 'Admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('adminpass123')
        admin_user.save()

        demo_user, _ = User.objects.get_or_create(
            username='demouser',
            defaults={
                'email': 'user@booking.local',
                'first_name': 'Alex',
                'last_name': 'Morgan',
                'role': 'user',
            }
        )
        demo_user.set_password('demopass123')
        demo_user.save()

        # 2. Categories
        cat_conf, _ = ResourceCategory.objects.get_or_create(
            name='Conference Rooms',
            defaults={'description': 'Meeting and presentation spaces equipped with full AV', 'icon': 'bi-building', 'color': '#2563EB', 'order': 1}
        )
        cat_desk, _ = ResourceCategory.objects.get_or_create(
            name='Workstations & Desks',
            defaults={'description': 'Quiet hot desks and dedicated workstations', 'icon': 'bi-laptop', 'color': '#059669', 'order': 2}
        )
        cat_media, _ = ResourceCategory.objects.get_or_create(
            name='Media Studios',
            defaults={'description': 'Audio & video recording facilities', 'icon': 'bi-camera-video', 'color': '#D97706', 'order': 3}
        )
        cat_event, _ = ResourceCategory.objects.get_or_create(
            name='Event Spaces',
            defaults={'description': 'Large halls for workshops, keynotes, and events', 'icon': 'bi-award', 'color': '#7C3AED', 'order': 4}
        )

        # 3. 16 Detailed Resources
        resources_data = [
            # Conference Rooms (4)
            {
                'slug': 'executive-boardroom-a',
                'name': 'Executive Boardroom A',
                'category': cat_conf,
                'location': 'Building A - Floor 3',
                'capacity': 16,
                'amenities': ['4K Display', 'Video Conferencing', 'Whiteboard', 'Coffee Bar'],
                'buffer_minutes': 15,
                'description': 'High-end meeting space with 4K display, video conferencing phone, and executive leather seating for 16.'
            },
            {
                'slug': 'innovation-lab',
                'name': 'Innovation Lab & Creative Hub',
                'category': cat_conf,
                'location': 'Building B - Floor 2',
                'capacity': 10,
                'amenities': ['Smart Screen', 'Glass Whiteboards', 'High-speed Wi-Fi', 'Ergonomic Chairs'],
                'buffer_minutes': 15,
                'description': 'Flexible collaborative space with writable glass walls, dual smart displays, and breakout lounge.'
            },
            {
                'slug': 'strategy-war-room',
                'name': 'Agile Strategy War Room',
                'category': cat_conf,
                'location': 'Building A - Floor 2',
                'capacity': 12,
                'amenities': ['Kanban Board', 'Interactive Screen', 'Post-it Station', 'Coffee Machine'],
                'buffer_minutes': 15,
                'description': 'Sprint room optimized for team planning, sticky-note brainstorming, and roadmap sprint reviews.'
            },
            {
                'slug': 'executive-boardroom-b',
                'name': 'Executive Boardroom B',
                'category': cat_conf,
                'location': 'Building C - Floor 4',
                'capacity': 20,
                'amenities': ['Dual 85" Screens', 'Cisco TelePresence', 'Polycom Mic', 'Catering Counter'],
                'buffer_minutes': 20,
                'description': 'Large enterprise boardroom equipped with dual 85" 4K displays and Cisco video conferencing.'
            },

            # Media Studios (4)
            {
                'slug': 'podcast-studio-b',
                'name': 'Podcast & Audio Studio B',
                'category': cat_media,
                'location': 'Media Complex - Studio B',
                'capacity': 4,
                'amenities': ['Acoustic Isolation', '4x Shure SM7B Mics', 'Rodecaster Console', 'Air Conditioning'],
                'buffer_minutes': 30,
                'description': 'Soundproofed acoustic booth equipped with 4 Shure SM7B mics, multi-track mixer, and studio lighting.'
            },
            {
                'slug': 'video-shoot-stage-a',
                'name': 'Video Shoot & Green Screen Stage',
                'category': cat_media,
                'location': 'Media Complex - Stage A',
                'capacity': 8,
                'amenities': ['Green Screen Wall', '4K Cinema Cameras', 'Teleprompter', 'DMX Lighting Grid'],
                'buffer_minutes': 45,
                'description': 'Full video production suite with cyclorama green screen wall, cinema lighting grid, and teleprompter.'
            },
            {
                'slug': 'photography-product-studio',
                'name': 'Photography & Product Studio C',
                'category': cat_media,
                'location': 'Media Complex - Studio C',
                'capacity': 6,
                'amenities': ['Softbox Lighting', 'Seamless Paper Rolls', 'High-End Props', 'Styling Counter'],
                'buffer_minutes': 30,
                'description': 'Professional photography studio tailored for commercial product shoots, headshots, and editorial.'
            },
            {
                'slug': 'livestream-broadcasting-booth',
                'name': 'Livestream & Broadcast Control Booth',
                'category': cat_media,
                'location': 'Media Complex - Booth D',
                'capacity': 3,
                'amenities': ['Stream Deck', 'Dual-PC Streaming Rig', 'Fiber Ethernet', 'Multi-Cam Switcher'],
                'buffer_minutes': 20,
                'description': 'Turnkey broadcasting booth for webinars, gaming streams, live product launches, and virtual keynotes.'
            },

            # Workstations & Pods (4)
            {
                'slug': 'quiet-desk-105',
                'name': 'Hot Desk #105 (Quiet Zone)',
                'category': cat_desk,
                'location': 'Open Office - 1st Floor',
                'capacity': 1,
                'amenities': ['Dual 4K Monitors', 'Electric Standing Desk', 'Gigabit Ethernet'],
                'buffer_minutes': 0,
                'description': 'Single-person ergonomic workstation with dual 27" 4K monitors and USB-C docking hub.'
            },
            {
                'slug': 'quiet-desk-106',
                'name': 'Hot Desk #106 (Developer Desk)',
                'category': cat_desk,
                'location': 'Open Office - 1st Floor',
                'capacity': 1,
                'amenities': ['UltraWide 38" Monitor', 'Ergonomic Mesh Chair', 'Fast Wi-Fi 6E'],
                'buffer_minutes': 0,
                'description': 'High-performance developer desk with 38" curved ultrawide monitor and mechanical keyboard dock.'
            },
            {
                'slug': 'video-conferencing-pod-3',
                'name': 'Focus Pod #3 (Private Phone)',
                'category': cat_desk,
                'location': 'Building A - Floor 2',
                'capacity': 2,
                'amenities': ['Acoustic Door', 'HD Camera', 'Ring Light', 'Power Outlets'],
                'buffer_minutes': 10,
                'description': 'Private sound-isolated booth designed for confidential 1-on-1 video calls and interviews.'
            },
            {
                'slug': 'video-conferencing-pod-4',
                'name': 'Focus Pod #4 (Executive Suite)',
                'category': cat_desk,
                'location': 'Building B - Floor 3',
                'capacity': 2,
                'amenities': ['Active Noise Isolation', '4K Cam', 'Adjustable Lighting', 'HEPA Air Filter'],
                'buffer_minutes': 10,
                'description': 'Premium noise-isolated booth with active ventilation and 4K webcam for executive video calls.'
            },

            # Event Venues (4)
            {
                'slug': 'grand-auditorium',
                'name': 'Grand Auditorium & Keynote Hall',
                'category': cat_event,
                'location': 'Main Hall - Ground Floor',
                'capacity': 150,
                'amenities': ['PA Sound System', 'Stage Lighting', 'Dual 4K Projectors', 'Green Room', 'VIP Seating'],
                'buffer_minutes': 60,
                'description': 'Spacious event venue suitable for company all-hands, product launches, and developer keynotes.'
            },
            {
                'slug': 'rooftop-terrace-lounge',
                'name': 'Skyline Outdoor Event Terrace',
                'category': cat_event,
                'location': 'Rooftop - Tower C',
                'capacity': 75,
                'amenities': ['Outdoor Heaters', 'Bar Station', 'Surround Sound', 'Panoramic View'],
                'buffer_minutes': 45,
                'description': 'Scenic rooftop space ideal for evening team socials, networking mixers, and celebration dinners.'
            },
            {
                'slug': 'glass-pavilion-banquet-hall',
                'name': 'Glass Pavilion & Banquet Hall',
                'category': cat_event,
                'location': 'Building C - Garden Wing',
                'capacity': 100,
                'amenities': ['Banquet Seating', 'Catering Kitchen', 'Ambient Lighting', 'Stage Setup'],
                'buffer_minutes': 60,
                'description': 'Glass-walled event hall with garden views, full catering access, and customizable banquet layouts.'
            },
            {
                'slug': 'exhibition-workshop-gallery',
                'name': 'Exhibition & Workshop Gallery',
                'category': cat_event,
                'location': 'Building A - Gallery Hall',
                'capacity': 60,
                'amenities': ['Modular Partition Walls', 'Interactive Touch Screens', 'Workshop Tables', 'Buffet Setup'],
                'buffer_minutes': 30,
                'description': 'Open-plan gallery for hackathons, interactive workshops, art exhibitions, and pop-up events.'
            }
        ]

        created_resources = []
        for rdata in resources_data:
            res, _ = Resource.objects.get_or_create(
                slug=rdata['slug'],
                defaults={
                    'name': rdata['name'],
                    'category': rdata['category'],
                    'location': rdata['location'],
                    'capacity': rdata['capacity'],
                    'amenities': rdata['amenities'],
                    'buffer_minutes': rdata['buffer_minutes'],
                    'description': rdata['description'],
                    'created_by': admin_user,
                }
            )
            created_resources.append(res)

        # 4. Availability Rules
        for res in created_resources:
            for day in range(5):
                AvailabilityRule.objects.get_or_create(
                    resource=res,
                    weekday=day,
                    start_time=datetime.time(8, 0),
                    end_time=datetime.time(20, 0),
                )

        # 5. Bookings
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        
        b1_start = now.replace(hour=10)
        b1_end = b1_start + datetime.timedelta(hours=2)
        if not Booking.objects.filter(resource=created_resources[0], start_datetime=b1_start).exists():
            Booking.objects.create(
                resource=created_resources[0],
                user=demo_user,
                title='Q3 Product Strategy Review',
                description='Quarterly alignment with engineering & design leads.',
                start_datetime=b1_start,
                end_datetime=b1_end,
                attendees=12,
                status=Booking.Status.CONFIRMED,
            )

        b2_start = (now + datetime.timedelta(days=1)).replace(hour=14)
        b2_end = b2_start + datetime.timedelta(hours=1, minutes=30)
        if not Booking.objects.filter(resource=created_resources[4], start_datetime=b2_start).exists():
            Booking.objects.create(
                resource=created_resources[4],
                user=demo_user,
                title='Podcast Ep. 42 Recording',
                description='Recording episode on cloud infrastructure scalability.',
                start_datetime=b2_start,
                end_datetime=b2_end,
                attendees=3,
                status=Booking.Status.CONFIRMED,
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded 16 resources, availability rules, and active bookings!'))
